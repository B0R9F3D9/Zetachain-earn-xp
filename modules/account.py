import asyncio, time, random
from loguru import logger

from web3 import AsyncWeb3, Account as Web3Account
from eth_account import Account as EthereumAccount
from web3.exceptions import TransactionNotFound
from web3.middleware import async_geth_poa_middleware

from settings import GAS_MULTIPLIER, RPC, EXPLORER
from config import ERC20_ABI, TOKENS
from utils import retry, sleep

Web3Account.enable_unaudited_hdwallet_features()


class Account:
    def __init__(self, account_id: int, key_mnemonic: str, proxy: str | None = None, withdraw_address: str | None = None) -> None:
        self.account_id = account_id
        self.explorer = EXPLORER
        self.proxy = f'http://{proxy}' if proxy else None
        self.w3 = AsyncWeb3(provider=AsyncWeb3.AsyncHTTPProvider(RPC, request_kwargs={'proxy': self.proxy}), middlewares=[async_geth_poa_middleware])
        self.private_key = key_mnemonic if key_mnemonic.startswith('0x') else self.w3.eth.account.from_mnemonic(mnemonic=key_mnemonic).key.hex()
        self.account = EthereumAccount.from_key(self.private_key)
        self.address = AsyncWeb3.to_checksum_address(self.account.address)
        self.withdraw_address = AsyncWeb3.to_checksum_address(withdraw_address) if withdraw_address else None
        
        self.addr = f"{self.address[:5]}...{self.address[-5:]}"
        self.withdr_addr = f"{self.withdraw_address[:5]}...{self.withdraw_address[-5:]}" if withdraw_address else 'Не указан'
        self.prox = self.proxy.split('@')[1] if proxy else 'Не указан'
        self.info = f"[№{self.account_id} - {self.address[:5]}...{self.address[-5:]}]"

    async def check_allowance(self, token_address: str, contract_address: str) -> int:
        token_address = self.w3.to_checksum_address(token_address)
        contract_address = self.w3.to_checksum_address(contract_address)
        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        amount_approved = await contract.functions.allowance(self.address, contract_address).call()
        return amount_approved
    
    @retry
    async def approve(self, amount_wei: int, token_address: str, contract_address: str) -> None:
        token_address = self.w3.to_checksum_address(token_address)
        contract_address = self.w3.to_checksum_address(contract_address)
        contract = self.w3.eth.contract(address=token_address, abi=ERC20_ABI)
        allowance_amount = await self.check_allowance(token_address, contract_address)
        if allowance_amount < amount_wei:
            logger.info(f"{self.info} Делаю аппрув...")
            tx_data = await self.get_tx_data()
            transaction = await contract.functions.approve(contract_address, amount_wei).build_transaction(tx_data)
            await self.send_txn(transaction)
            await sleep(10, 15)
        else:
            logger.info(f'{self.info} Аппрув уже есть, пропускаю')

    async def get_tx_data(self, value: int = 0) -> dict:
        return {
            "from": self.address,
            "value": value,
            "nonce": await self.w3.eth.get_transaction_count(self.address),
            "gasPrice": await self.w3.eth.gas_price,
            "chainId": await self.w3.eth.chain_id
        }

    def get_contract(self, contract_address: str, abi: dict | None = None) -> object:
        contract_address = self.w3.to_checksum_address(contract_address)
        if abi is None:
            abi = ERC20_ABI
        return self.w3.eth.contract(address=contract_address, abi=abi)

    async def get_balance(self, token_symbol: str | None = None) -> dict:
        if token_symbol == 'ZETA' or not token_symbol:
            balance_wei = await self.w3.eth.get_balance(self.address)
            return {"balance_wei": balance_wei, "balance": balance_wei/10**18, "symbol": 'ZETA', "decimal": 18}
        contract_address = TOKENS[token_symbol]
        contract = self.get_contract(contract_address)
        symbol = await contract.functions.symbol().call()
        decimal = await contract.functions.decimals().call()
        balance_wei = await contract.functions.balanceOf(self.address).call()
        return {"balance_wei": balance_wei, "balance": balance_wei / 10**decimal, "symbol": symbol, "decimal": decimal}
    
    async def wait_until_tx_finished(self, hash: str, max_wait_time=60) -> bool:
        start_time = time.time()
        while True:
            try:
                receipts = await self.w3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")
                if status == 1:
                    logger.success(f"{self.info} Транзакция успешна! {self.explorer+hash}")
                    return True
                elif status is None:
                    await asyncio.sleep(0.3)
                else:
                    logger.error(f"{self.info} Транзакция не удалась! {self.explorer+hash}")
                    return False
            except TransactionNotFound:
                if time.time() - start_time > max_wait_time:
                    logger.error(f"{self.info} Транзакция не найдена! {self.explorer+hash}")
                    return False
                await asyncio.sleep(1)

    async def sign(self, transaction: dict) -> dict:
        gas = await self.w3.eth.estimate_gas(transaction)
        gas = int(gas * random.uniform(*GAS_MULTIPLIER))
        transaction.update({"gas": gas})
        return self.w3.eth.account.sign_transaction(transaction, self.private_key)

    async def send_raw_transaction(self, signed_txn: dict) -> str:
        txn_hash = await self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        return txn_hash
    
    async def send_txn(self, txn) -> None:
        signed_txn = await self.sign(txn)
        txn_hash = await self.send_raw_transaction(signed_txn)
        result = await self.wait_until_tx_finished(txn_hash.hex())
        if not result:
            raise Exception("Транзакция не удалась!")
    
    @retry
    async def transfer_zeta(self, value: float, receiver_address: str | None = None) -> None:
        if receiver_address is None:
            receiver_address = self.address
        receiver_address = self.w3.to_checksum_address(receiver_address)
        logger.info(f"{self.info} Отправляем {value:.5f} ZETA на {receiver_address[:5]}...{receiver_address[-5:]}")
        tx_data = await self.get_tx_data(int(value * 10**18)) | {"to": receiver_address, 'data': '0x'}
        await self.send_txn(tx_data)

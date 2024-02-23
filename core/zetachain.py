import asyncio, random, aiohttp
from loguru import logger
from base64 import b64decode
from hexbytes import HexBytes
from fake_useragent import UserAgent

from web3 import AsyncWeb3
from web3.contract.async_contract import AsyncContract
from eth_account.messages import encode_structured_data

from .account import Account
from settings import *
from config import *
from .helpers import retry
from .okx import OKX


class Zetachain:
    def __init__(self, acc: Account) -> None:
        self.acc: Account = acc
        self.w3: AsyncWeb3 = self.acc.w3
        self.izumi_quoter_contract: AsyncContract = self.acc.get_contract(CONTRACTS['izumi_quoter'], IZUMI_QUOTER_ABI)
        self.izumi_router_contract: AsyncContract = self.acc.get_contract(CONTRACTS['izumi_router'], IZUMI_ROUTER_ABI)
        self.zetahub_contract: AsyncContract = self.acc.get_contract(CONTRACTS['zetahub'], ZETAHUB_ABI)
        self.stzeta_contract: AsyncContract = self.acc.get_contract(CONTRACTS['stzeta'], STZETA_ABI)
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://hub.zetachain.com',
            'referer': 'https://hub.zetachain.com/',
            'user-agent': UserAgent().random
        }

    @retry
    async def check_complete(self, task_name: str) -> bool:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f'https://xp.cl04.zetachain.com/v1/get-user-has-xp-to-refresh', params={'address': self.acc.address}, proxy=self.acc.proxy) as resp:
                if resp.status == 400 and 'not verified' in (await resp.text()).lower():
                    raise Exception(f'{self.acc.info} Кошелёк не зарегистрирован! | Повторная проверка через 20-30 сек')
                elif resp.status == 429:
                    raise Exception(f'{self.acc.info} Лимит запросов! | Повторная попытка через 20-30 сек')
                elif resp.status != 200: logger.error(f'{self.acc.info} Код: {resp.status} | Ответ: {await resp.text()}'); return
                data = (await resp.json())['xpRefreshTrackingByTask'][task_name]
        return data['hasAlreadyEarned'] is False and data['hasXpToRefresh'] is False
    
    @retry
    async def check_enroll(self) -> bool:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.post(f"https://xp.cl04.zetachain.com/v1/enroll-in-zeta-xp", json={'address': self.acc.address}, proxy=self.acc.proxy) as resp:
                if resp.status == 429: raise Exception(f'{self.acc.info} Лимит запросов! | Повторная попытка через 20-30 сек')
                elif resp.status != 200: raise Exception(f'{self.acc.info} Код: {resp.status} | Ответ: {await resp.text()}')
                return (await resp.json())['isUserVerified']
        
    @retry
    async def enroll(self) -> None:
        if not DO_ACTION_ANYWAY:
            if await self.check_enroll():
                logger.info(f'{self.acc.info} Кошелёк уже зарегистрирован ✅')
                return False
        logger.info(f'{self.acc.info} Делаю регистрацию...')
        address, expiration, r, s, v = b64decode(REF_LINK.split('code=')[1][:-1]).decode().split('&')
        address = address.split('=')[1][2:]
        expiration = self.w3.to_hex(int(expiration.split('=')[1]))[2:]
        r = r.split('=')[1][2:]
        s = s.split('=')[1][2:]
        v = self.w3.to_hex(int(v.split('=')[1][:2]))[2:]
        data = f"0xb9daad50000000000000000000000000{address.lower()}00000000000000000000000000000000000000000000000000000000{expiration}00000000000000000000000000000000000000000000000000000000000000{v}{r}{s}"
        tx_data = await self.acc.get_tx_data() | {'to': CONTRACTS['enroll'], 'data': data}
        await self.acc.send_txn(tx_data)
        await asyncio.sleep(10)
        result = await self.check_enroll()
        if result: return True
        else: raise Exception(f'{self.acc.info} Регистрация не удалась!')

    @retry
    async def transfer(self) -> None:
        if not DO_ACTION_ANYWAY:
            if not await self.check_complete('SEND_ZETA'):
                logger.info(f'{self.acc.info} Кошелёк уже переводил ZETA ✅')
                return
        amount = random.uniform(*TRANSFER_AMOUNT)
        await self.acc.transfer_zeta(amount)

    @retry
    async def izumi_swap(self, pair: str) -> None:
        if not DO_ACTION_ANYWAY:
            if not await self.check_complete(f'RECEIVE_{pair.split("/")[1].split(".")[0]}'):
                logger.info(f'{self.acc.info} Кошелёк уже свапал {pair} ✅')
                return
        fee = {'ZETA/BNB.BSC': 10000, 'ZETA/ETH.ETH': 3000, 'ZETA/BTC.BTC': 10000}[pair]
        amount = random.uniform(*SWAP_AMOUNT)
        logger.info(f'{self.acc.info} Делаю свап на iZUMi {amount:.5f} {pair}')

        from_token_bytes = HexBytes(SWAP_TOKENS[pair.split('/')[0]]).rjust(20, b'\0')
        to_token_bytes = HexBytes(SWAP_TOKENS[pair.split('/')[1]]).rjust(20, b'\0')
        fee_bytes = fee.to_bytes(3, 'big')
        path = from_token_bytes + fee_bytes + to_token_bytes

        data = self.izumi_quoter_contract.encodeABI(
            fn_name='swapAmount',
            args=[(
                path,
                self.acc.address,
                int(amount*10**18),
                10 if pair in ['ZETA/ETH.ETH', 'ZETA/BNB.BSC'] else 3,
                int((await self.w3.eth.get_block("latest"))['timestamp'] + 3600)
            )]
        )
        tx_data = self.izumi_router_contract.encodeABI(fn_name='multicall', args=[[data, "0x12210e8a"]])
        txn = await self.acc.get_tx_data(int(amount*10**18)) | {'to': CONTRACTS['izumi_router'], 'data': tx_data}
        await self.acc.send_txn(txn)

    @retry
    async def izumi_liquidity(self, pair: str) -> None:
        if not DO_ACTION_ANYWAY:
            if not await self.check_complete('POOL_DEPOSIT_ANY_POOL'):
                logger.info(f'{self.acc.info} Кошелёк уже добавлял ликвидность ✅')
                return False

        token_to = pair.split('/')[1]
        token_balance = (await self.acc.get_balance(token_to))['balance_wei']
        amount_wei = int(token_balance * random.uniform(0.1, 0.9)) # кол-во добавляемое в ликву - 10-90% от баланса токена
        zeta_amount_wei = int(amount_wei * random.uniform(0.5, 3)) # вроде лучше высчитать по курсу, но пох
        approve_amount = int(random.uniform(0.1, 111) * 10**18) # или amount_wei, но удобнее аппрув на дохуя 
        await self.acc.approve(approve_amount, USUAL_TOKENS[token_to], CONTRACTS['zetahub'])

        logger.info(f'{self.acc.info} Добавляю {amount_wei/10**18:.7f} {token_to} + {zeta_amount_wei/10**18:.7f} ZETA в iZUMi ликвидность...')
        txn = await self.zetahub_contract.functions.addLiquidityETH(
            USUAL_TOKENS[token_to],
            amount_wei,
            0, 0,
            self.acc.address,
            (await self.w3.eth.get_block("latest"))['timestamp'] + 3600
        ).build_transaction(await self.acc.get_tx_data(zeta_amount_wei))
        await self.acc.send_txn(txn)
        return True

    @retry
    async def mint_stzeta(self) -> None:
        if not DO_ACTION_ANYWAY:
            if not await self.check_complete('ACCUMULATED_FINANCE_DEPOSIT'):
                logger.info(f'{self.acc.info} Кошелёк уже делал минт $stZETA ✅')
                return False
        
        amount = random.uniform(*STZETA_MINT_AMOUNT)
        amount_wei = int(amount * 10**18)
        logger.info(f'{self.acc.info} Делаю минт {amount:.5f} $stZETA')

        txn = await self.stzeta_contract.functions.deposit(
            self.acc.address
        ).build_transaction(await self.acc.get_tx_data(amount_wei))
        await self.acc.send_txn(txn)

    @retry
    async def sign_message(self) -> str:
        data = {
            "types": {
                "Message": [{"name": "content", "type": "string"}],
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"}
                ]
            },
            "domain": {"name": "Hub/XP", "version": "1", "chainId": 7000},
            "primaryType": "Message",
            "message": {"content": "Claim XP"}
        }
        signature = self.w3.eth.account.sign_message(encode_structured_data(data), private_key=self.acc.private_key)
        return signature.signature.hex()

    @retry
    async def claim(self) -> None:
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f'https://xp.cl04.zetachain.com/v1/get-user-has-xp-to-refresh?address={self.acc.address}', proxy=self.acc.proxy) as resp:
                if resp.status != 200: logger.error(f'{self.acc.info} Ответ сервера: {resp.status}'); return
                data = await resp.json()
            tasks = [[key, value['xp']] for key, value in data["xpRefreshTrackingByTask"].items() if value["hasXpToRefresh"]]
            if not tasks:
                logger.info(f'{self.acc.info} Кошелёк уже заклеймил все доступные поинты ✅')
                return
            
            logger.info(f'{self.acc.info} Клеймлю {sum([task[1] for task in tasks])} поинтов...')
            points = 0
            for task in tasks:
                for attempt in range(RETRY_COUNT):
                    signature = await self.sign_message()
                    json_data = {'address': self.acc.address, 'signedMessage': signature, 'task': task[0]}
                    async with session.post('https://xp.cl04.zetachain.com/v1/xp/claim-task', json=json_data, proxy=self.acc.proxy) as resp:
                        data = await resp.json()
                    if data['message'] == 'XP refreshed successfully':
                        points += task[1]
                        logger.info(f'{self.acc.info} Заклеймил {task[1]} поинтов за {task[0]} ✅')
                        await asyncio.sleep(random.uniform(7, 10))
                        break
                    else:
                        logger.error(f'{self.acc.info} Не удалось заклеймить поинты для {task[0]}! Код: {resp.status} Ответ: {data}')
                        await asyncio.sleep(random.uniform(10, 15))
                        continue
        logger.success(f'{self.acc.info} Успешно заклеймил {points} поинтов 🎉')

    @retry
    async def withdraw(self) -> None:
        balance = (await self.acc.get_balance("ZETA"))["balance"]
        amount = balance - random.uniform(*AMOUNT_TO_SAVE)
        if not self.acc.withdraw_address:
            logger.error(f'{self.acc.info} Не указан адрес для вывода!')
            return
        return await self.acc.transfer_zeta(amount, self.acc.withdraw_address)

    @retry
    async def check(self) -> dict:
        base_return = {'№': self.acc.account_id, 'Адрес': self.acc.addr, 'Адрес для вывода': self.acc.withdr_addr,
                       'Прокси': self.acc.prox, 'Баланс': f'{(await self.acc.get_balance("ZETA"))["balance"]:.4f}'}
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(f'https://xp.cl04.zetachain.com/v1/get-user-has-xp-to-refresh?address={self.acc.address}', proxy=self.acc.proxy) as resp:
                if resp.status != 200:
                    if resp.status == 400: text = 'НеРегнут'
                    elif resp.status == 429: text = 'Подожди'
                    else: text = resp.status
                    return {**base_return, 'Поинтов': text, 'На клейм': text, **{task: text for task in TASKS_NAMES.values()}}
                data = (await resp.json())['xpRefreshTrackingByTask']
        points = 0; claim = 0
        result = {}
        for task in data:
            if task not in TASKS_NAMES: continue
            if data[task]['hasXpToRefresh']: claim += data[task]['xp']
            if data[task]['hasAlreadyEarned']: points += data[task]['xp']
            result[TASKS_NAMES[task]] = '✅' if data[task]['hasXpToRefresh'] or data[task]['hasAlreadyEarned'] else '❌'
        return {**base_return, 'Поинтов': points, 'На клейм': claim, **result}
    
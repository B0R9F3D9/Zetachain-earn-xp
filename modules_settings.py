import random
from questionary import select
from loguru import logger

from core import *
from settings import *


async def get_pair() -> str:
    result = await select(
        message="Выберите пару: ",
        instruction='(используйте стрелочки для навигации)',
        choices=['ZETA/BNB.BSC', 'ZETA/ETH.ETH', 'ZETA/BTC.BTC', 'Рандомная'],
        qmark="\n❓ ",
        pointer="👉 "
    ).ask_async()
    if result == 'Рандомная':
        return random.choice(['ZETA/BNB.BSC', 'ZETA/ETH.ETH', 'ZETA/BTC.BTC'])
    else: return result

async def work(zetachain: Zetachain) -> None:
    okx = OKX(zetachain.acc.info)
    await okx_withdraw(zetachain)

    enroll_result = await zetachain.enroll()
    if enroll_result: await sleep(20, 30)

    await zetachain.transfer()

    pairs = ['ZETA/BNB.BSC', 'ZETA/ETH.ETH', 'ZETA/BTC.BTC']
    random.shuffle(pairs)
    [await zetachain.izumi_swap(pair) for pair in pairs]

    luquidity_result = await zetachain.add_liquidity(random.choice(pairs))
    if luquidity_result: await sleep(30, 35)

    await zetachain.claim()

    tx_hash = await zetachain.withdraw()
    await okx.wait_for_deposit('ZETA', 'ZetaChain', tx_hash)

async def custom_way(zetachain: Zetachain) -> None:
    for action in CUSTOM_WAY:
        if action == 'okx_withdraw': await okx_withdraw(zetachain)
        if 'izumi_swap' in action or 'add_liquidity' in action: action, pair = action.split('-')
        else: pair = None
        result = await run_solo_module(action, zetachain, pair)
        if ('enroll' in action or 'add_liquidity' in action) and result: await sleep(20, 30)

async def run_solo_module(module: str, zetachain: Zetachain, pair: str | None = None) -> bool | None:
    if 'izumi_swap' in module or 'add_liquidity' in module:
        if not pair: pair = await get_pair()
        return await getattr(zetachain, module)(pair)
    return await getattr(zetachain, module)()

async def okx_withdraw(zetachain: Zetachain) -> None:
    okx = OKX(zetachain.acc.info)
    if (await zetachain.acc.get_balance('ZETA'))['balance'] < MIN_WALLET_BALANCE:
        amount = random.uniform(*AMOUNT_TO_WITHDRAW)
        await okx.withdraw(zetachain.acc.address, amount, 'ZETA', 'ZetaChain')
    else: logger.info(f'{zetachain.acc.info} Аккаунт уже имеет более {MIN_WALLET_BALANCE} ZETA')

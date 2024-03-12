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
    else:
        return result

async def work(zetachain: Zetachain) -> None:
    if USE_OKX: okx = OKX(zetachain.acc.info); await okx_withdraw(zetachain)

    await zetachain.check_tasks()
    enroll_result = await zetachain.enroll()
    if enroll_result: await sleep(20, 30)

    await zetachain.transfer()

    pairs = ['ZETA/BNB.BSC', 'ZETA/ETH.ETH', 'ZETA/BTC.BTC']
    random.shuffle(pairs)
    for pair in pairs: await zetachain.izumi_swap(pair)

    await zetachain.izumi_liquidity(random.choice(pairs))
    await zetachain.eddy_swap(random.choice(pairs))
    await zetachain.mint_stzeta()
    await zetachain.ultiverse_mint()

    await sleep(30, 45)
    await zetachain.claim()
    tx_hash = await zetachain.withdraw()
    if USE_OKX: await okx.wait_for_deposit('ZETA', 'ZetaChain', tx_hash)

async def custom_way(zetachain: Zetachain) -> None:
    for action in CUSTOM_WAY:
        if action == 'okx_withdraw':
            await okx_withdraw(zetachain)
            continue
        pair = None
        if 'swap' in action or 'liquidity' in action:
            action, pair = action.split('-')
        result = await run_solo_module(action, zetachain, pair)
        if result: await sleep(20, 30)

async def run_solo_module(module: str, zetachain: Zetachain, pair: str | None = None) -> bool | None:
    if zetachain.tasks == {}:await zetachain.check_tasks()
    if 'swap' in module or 'liquidity' in module:
        if not pair: pair = await get_pair()
        return await getattr(zetachain, module)(pair)
    await getattr(zetachain, module)()

async def okx_withdraw(zetachain: Zetachain) -> None:
    if not USE_OKX:
        logger.error(f'Вывод невозможен! ОКХ выключен в настройках')
        return
    okx = OKX(zetachain.acc.info)
    if (await zetachain.acc.get_balance('ZETA'))['balance'] < MIN_WALLET_BALANCE:
        amount = random.uniform(*AMOUNT_TO_WITHDRAW)
        await okx.withdraw(zetachain.acc.address, amount, 'ZETA', 'ZetaChain')
    else:
        logger.info(f'{zetachain.acc.info} Аккаунт уже имеет более {MIN_WALLET_BALANCE} ZETA')

async def get_okx_balance():
    if not USE_OKX: 
        logger.error(f'Не удалось получить баланс OKX! ОКХ выключен в настройках')
        return
    okx = OKX('')
    balance = await okx.get_okx_ccy_balance('ZETA')
    logger.info(f'Баланс OKX: {balance} $ZETA')
    return balance

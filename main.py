import random, asyncio
from sys import stderr
from datetime import datetime
from loguru import logger
from questionary import Choice, select
from tabulate import tabulate

from config import ACCOUNTS, PROXIES, WITHDRAW_ADDRESSES
from utils import wait_for_new_ip, sleep
from modules import *
from settings import *


async def checker(zetachains: list[Zetachain]) -> None:
    tasks = [loop.create_task(zetachain.check()) for zetachain in zetachains]
    result = await asyncio.gather(*tasks)
    result.sort(key=lambda x: x['№'])
    print(tabulate(result, headers="keys", tablefmt="rounded_grid"))

def select_zetachains(zetachains: list[Zetachain]) -> list[Zetachain]:
    if len(zetachains) == 1: return zetachains
    print('Выберите аккаунты для работы. Формат: \n'
        '1 — для выбора только первого аккаунта\n'
        '1,2,3 — для выбора первого, второго и третьего аккаунта\n'
        '1-3 — для выбора аккаунтов от первого до третьего включительно\n'
        'all — для выбора всех аккаунтов (или нажмите Enter)\n')
    result = input('Введите ваш выбор: ')
    if result == 'all' or result == '': return zetachains
    try:
        if ',' in result:
            return [zetachains[int(i) - 1] for i in result.split(',')]
        elif '-' in result:
            return zetachains[int(result.split('-')[0]) - 1:int(result.split('-')[1])]
        elif '-' not in result and ',' not in result:
            return [zetachains[int(result) - 1]]
    except ValueError:
        raise ValueError('Некорректный выбор аккаунтов!')

async def get_module() -> str:
    result = await select(
        message="Выберите модуль для работы: ",
        instruction='(используйте стрелочки для навигации)',
        choices=[
            Choice("🧠 Автоматический Маршрут", 'work'),
            Choice("🧠 Кастомный маршрут", 'custom_way'),
            Choice("📝 Регистрация", 'enroll'),
            Choice("💸 Перевод", 'transfer'),
            Choice("🔄 Свап ZETA/BNB.BSC", 'izumi_swap-ZETA/BNB.BSC'),
            Choice("🔄 Свап ZETA/ETH.ETH", 'izumi_swap-ZETA/ETH.ETH'),
            Choice("🔄 Свап ZETA/BTC.BTC", 'izumi_swap-ZETA/BTC.BTC'),
            Choice("➕ Добавить ZETA/BNB.BSC ликвидность", 'add_liquidity'),
            Choice("🎁 Клейм поинтов", 'claim'),
            Choice("💰 Вывод", 'withdraw'),
            Choice("📊 Чекер", 'checker'),
            Choice("🔙 Вернуться к выбору аккаунтов", 'back'),
            Choice("❌ Выход", "exit"),
        ],
        qmark="\n❓ ",
        pointer="👉 "
    ).ask_async()
    return result

async def run_module(module: str, zetachain: Zetachain) -> None:
    if module == 'work':
        enroll = await zetachain.enroll()
        if enroll: await sleep(20, 25) 
        await zetachain.transfer()
        swaps = ['ZETA/BNB.BSC', 'ZETA/ETH.ETH', 'ZETA/BTC.BTC']
        random.shuffle(swaps)
        [await zetachain.izumi_swap(swap) for swap in swaps]
        liquidity = await zetachain.add_liquidity()
        if liquidity: await sleep(25, 30)
        await zetachain.claim()
    elif 'izumi_swap' in module:
        way = module.split('-')[1]
        await zetachain.izumi_swap(way)
    elif 'custom_way' in module:
        for action in CUSTOM_WAY:
            if 'izumi_swap' in action: await zetachain.izumi_swap(action.split('-')[1])
            else: result = await getattr(zetachain, action)()
            if action in ['enroll', 'add_liquidity'] and result: await sleep(25, 30)
    else:
        await getattr(zetachain, module)()


async def main(zetachains: list[Zetachain]) -> None:
    module = await get_module()
    if module == 'exit':
        raise KeyboardInterrupt
    elif module == 'checker':
        await checker(zetachains)
        return
    elif module == 'back':
        return True
    for zetachain in zetachains:
        await run_module(module, zetachain)
        if zetachain != zetachains[-1] and not zetachain.acc.proxy:
            await wait_for_new_ip()
        

if __name__ == '__main__':
    logger.remove()
    format='<white>{time:HH:mm:ss}</white> | <bold><level>{level: <7}</level></bold> | <level>{message}</level>'
    logger.add(sink=stderr, format=format)
    logger.add(sink=f'logs/{datetime.today().strftime("%Y-%m-%d")}.log', format=format)

    logger.info(f'Найдено: {len(ACCOUNTS)} аккаунтов, {len(PROXIES)} прокси, {len(WITHDRAW_ADDRESSES)} адресов для вывода')
    accs = [Account(_id, key_mnemonic, PROXIES.get(_id) if USE_PROXY else None, WITHDRAW_ADDRESSES.get(_id))
            for _id, key_mnemonic in enumerate(ACCOUNTS, 1)]

    if SHUFFLE_WALLETS:
        random.shuffle(accs)
        logger.warning('Аккаунты перемешаны')
    logger.warning('Используются прокси') if USE_PROXY else logger.warning('Прокси не используются')

    ZETACHAINS = [Zetachain(acc) for acc in accs]    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(checker(ZETACHAINS))
    zetachains = select_zetachains(ZETACHAINS)

    while True:
        try:
            result = loop.run_until_complete(main(zetachains))
            if result:
                zetachains = select_zetachains(ZETACHAINS)
        except KeyboardInterrupt:
           break
        except Exception as e:
           logger.critical(e)
           break

    print('👋👋👋')

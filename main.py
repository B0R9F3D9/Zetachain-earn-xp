import random, asyncio
from sys import stderr
from datetime import datetime
from loguru import logger
from questionary import Choice, select
from tabulate import tabulate

from config import ACCOUNTS, PROXIES, WITHDRAW_ADDRESSES
from core import *
from settings import *
from functions import *


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
    return await select(
        message="Выберите модуль для работы: ",
        instruction='(используйте стрелочки для навигации)',
        choices=[
            Choice("🧠 Автоматический Маршрут", 'work'),
            Choice("🧠 Кастомный маршрут", 'custom_way'),
            Choice("💲 Вывод с ОКХ", "okx_withdraw"),
            Choice("📝 Регистрация по рефке", 'enroll'),
            Choice("💸 Перевод самому себе", 'transfer'),
            Choice("🔄 Свап на iZUMi", 'izumi_swap'),
            Choice("➕ Добавить ликвидность на iZUMi", 'izumi_liquidity'),
            Choice("🎁 Клейм поинтов", 'claim'),
            Choice("🌹 Минт $stZETA", "mint_stzeta"),
            Choice("💰 Депозит на адрес для вывода", 'withdraw'),
            Choice("📊 Чекер", 'checker'),
            Choice("💹 Проверить баланс ОКХ", 'okx_balance'),
            Choice("🔙 Вернуться к выбору аккаунтов", 'back'),
            Choice("❌ Выход", "exit"),
        ],
        qmark="\n❓ ",
        pointer="👉 "
    ).ask_async()

async def main(zetachains: list[Zetachain]) -> None:
    module = await get_module()
    if module == 'exit':
        raise KeyboardInterrupt
    elif module == 'checker':
        await checker(zetachains)
        return
    elif module == 'back':
        return True
    elif module == 'okx_balance':
        await get_okx_balance()
        return
    for zetachain in zetachains:
        if module in ['work', 'custom_way', 'okx_withdraw']:
            await globals()[module](zetachain)
        else:
            await run_solo_module(module, zetachain)
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
    if DO_ACTION_ANYWAY: logger.warning('Действия выполняются в любом случае')

    ZETACHAINS = [Zetachain(acc) for acc in accs]    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_okx_balance()) if USE_OKX else logger.warning('OKX не используется')
    loop.run_until_complete(checker(ZETACHAINS))
    zetachains = select_zetachains(ZETACHAINS)

    while True:
        try:
            result = loop.run_until_complete(main(zetachains))
            if result:
                loop.run_until_complete(checker(ZETACHAINS))
                zetachains = select_zetachains(ZETACHAINS)
        except KeyboardInterrupt:
            break
        except Exception as e:
           logger.critical(e)
           break

    print('👋👋👋')

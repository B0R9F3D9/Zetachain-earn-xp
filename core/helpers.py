from loguru import logger
from settings import RETRY_COUNT
import asyncio, random, httpx


async def sleep(sleep_from: int, sleep_to: int):
    delay = random.randint(sleep_from, sleep_to)
    logger.info(f'Спим {delay} секунд...')
    for _ in range(delay):
        await asyncio.sleep(1)

def retry(func):
    async def wrapper(*args, **kwargs):
        for i in range(1, RETRY_COUNT+1):
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                logger.error(f'({i}/{RETRY_COUNT}): {e}')
                if i != RETRY_COUNT: await sleep(20, 30)
    return wrapper

@retry
async def wait_for_new_ip():
    async with httpx.AsyncClient() as client:
        resp = await client.get('https://api.ipify.org')
        ip = resp.text
    while True:
        try:
            logger.info(f'Текущий IP: {ip} | Нажмите Enter для обновления...')
            input()
            async with httpx.AsyncClient() as client:
                resp = await client.get('https://api.ipify.org')
                new_ip = resp.text
            if new_ip != ip:
                logger.success(f'IP изменился, новый: {new_ip}')
                return
            else:
                logger.error(f'IP не изменился!')
        except ConnectionAbortedError:
            pass
        except Exception as e:
            logger.error(f'Ошибка: {e}')

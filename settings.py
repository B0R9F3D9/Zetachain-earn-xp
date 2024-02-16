# Использовать прокси
USE_PROXY: bool = False

# Перемешать кошельки
SHUFFLE_WALLETS: bool = False

# Мин, макс мультипликатор газа для транзакций
GAS_MULTIPLIER: tuple[float, float] = (1, 1.069)

# Количество попыток для совершения действий
RETRY_COUNT: int = 3

# Делать действие в любом случае, даже если оно уже выполнено
DO_ACTION_ANYWAY: bool = False

# Кастомный маршрут (все модули уже записаны, их можно закомментировать или поменять местами)
CUSTOM_WAY: list[str] = [
    'enroll', # Регистрация
    'transfer', # Перевод самому себе
    'izumi_swap-ZETA/BTC.BTC', # Свап ZETA/BTC.BTC
    'izumi_swap-ZETA/BNB.BSC', # Свап ZETA/BNB.BSC
    'izumi_swap-ZETA/ETH.ETH', # Свап ZETA/ETH.ETH
    'add_liquidity', # Добавить ликвидность
    'claim', # Клейм поинтов
    'withdraw', # Вывод 
]

# Настройки маршрутов
TRANSFER_AMOUNT: tuple[float, float] = (0.000001, 0.0001) # Мин, Макс сумма перевода самому себе в $ZETA
SWAP_AMOUNT: tuple[float, float] = (0.00001, 0.001) # Мин, Макс сумма свапа в $ZETA
AMOUNT_TO_SAVE: tuple[float, float] = (0.01, 0.02) # Мин, Макс сумма для сохранения на кошельке в $ZETA

# Прочее
RPC: str = 'https://zetachain-evm.blockpi.network/v1/rpc/public'
EXPLORER: str = 'https://zetachain.blockscout.com/tx/'
REF_LINK: str = 'https://hub.zetachain.com/xp?code=YWRkcmVzcz0weGZjQUM1NGQ4QTc3NGM3OTAwOTJBNzJmNDFkYkYxOTFDODUzOGRCOUEmZXhwaXJhdGlvbj0xNzEwNTg0MjM0JnI9MHg4Mjg3MzBhMDhkZjIzMjcwODliMDEyMWI1YjU4MzA3NGYyNTRlN2UwZTQxMjMzOTcwZDA3YWEwN2ExOTNkYmMyJnM9MHg1YjMzNDQ4MjBjOGY5NTVhNWZiMWEzODdlN2ZlNjc3ZGNiMzE5Mjk2YjUzZTIxYTZjODc5OTExMzhlN2Q1YThhJnY9Mjg%3D'

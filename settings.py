# Использовать прокси
USE_PROXY: bool = True

# Использовать ОКХ для вывода на аккаунты и проверки депозита на адрес ОКХ
USE_OKX: bool = False

# Перемешать кошельки
SHUFFLE_WALLETS: bool = False

# Мин, макс мультипликатор газа для транзакций
GAS_MULTIPLIER: tuple[float, float] = (1, 1.1)

# Количество попыток для совершения действий
RETRY_COUNT: int = 5

# Делать действие в любом случае, даже если оно уже выполнено
DO_ACTION_ANYWAY: bool = False

# Кастомный маршрут (все модули уже записаны, их можно закомментировать или поменять местами)
CUSTOM_WAY: list[str] = [
    'okx_withdraw', # Вывод с ОКХ
    'enroll', # Регистрация
    'transfer', # Перевод самому себе
    'izumi_swap-ZETA/BNB.BSC', # Свап ZETA/BNB.BSC
    'izumi_swap-ZETA/ETH.ETH', # Свап ZETA/ETH.ETH
    'izumi_swap-ZETA/BTC.BTC', # Свап ZETA/BTC.BTC
    'izumi_liquidity-ZETA/BNB.BSC', # Добавить ликвидность ZETA/BNB.BSC
    'izumi_liquidity-ZETA/ETH.ETH', # Добавить ликвидность ZETA/ETH.ETH
    'izumi_liquidity-ZETA/BTC.BTC', # Добавить ликвидность ZETA/BTC.BTC
    'mint_stzeta', # Минт $stZETA
    'claim', # Клейм поинтов
    'withdraw', # Вывод на адрес для депозита
]

# Настройки маршрутов
MIN_WALLET_BALANCE: float = 0 # Минимальный баланс кошелька в $ZETA, если баланс меньше то будет выводить с ОКХ сумму AMOUNT_TO_WITHDRAW
TRANSFER_AMOUNT: tuple[float, float] = (0.000001, 0.0001) # Мин, Макс сумма перевода самому себе в $ZETA
SWAP_AMOUNT: tuple[float, float] = (0.00001, 0.001) # Мин, Макс сумма свапа в $ZETA
STZETA_MINT_AMOUNT: tuple[float, float] = (0.00001, 0.001) # Мин, Макс сумма минта $stZETA
AMOUNT_TO_SAVE: tuple[float, float] = (0.02, 0.03) # Мин, Макс сумма для сохранения на кошельке в $ZETA
AMOUNT_TO_WITHDRAW: tuple[float, float] = (2, 2.2) # Мин, Макс сумма для вывода с ОКХ (минимум 2 $ZETA)

# Прочее
RPC: str = 'https://zetachain-evm.blockpi.network/v1/rpc/public'
EXPLORER: str = 'https://zetachain.blockscout.com/tx/'
REF_LINK: str = 'https://hub.zetachain.com/xp?code=YWRkcmVzcz0weGZjQUM1NGQ4QTc3NGM3OTAwOTJBNzJmNDFkYkYxOTFDODUzOGRCOUEmZXhwaXJhdGlvbj0xNzEwNTg0MjM0JnI9MHg4Mjg3MzBhMDhkZjIzMjcwODliMDEyMWI1YjU4MzA3NGYyNTRlN2UwZTQxMjMzOTcwZDA3YWEwN2ExOTNkYmMyJnM9MHg1YjMzNDQ4MjBjOGY5NTVhNWZiMWEzODdlN2ZlNjc3ZGNiMzE5Mjk2YjUzZTIxYTZjODc5OTExMzhlN2Q1YThhJnY9Mjg%3D'

# OKX API (keep it secret)
OKX_API_KEY: str = ''
OKX_API_SECRET: str = ''
OKX_PASSPHRASE: str = ''

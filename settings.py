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
    'transfer', # Перевод самому себе $ZETA
    'izumi_swap-ZETA/BNB.BSC', # Свап iZUMi ZETA/BNB.BSC
    'izumi_swap-ZETA/ETH.ETH', # Свап iZUMi ZETA/ETH.ETH
    'izumi_swap-ZETA/BTC.BTC', # Свап iZUMi ZETA/BTC.BTC
    'eddy_swap-ZETA/BNB.BSC', # Свап Eddy Finance ZETA/BNB.BSC
    'eddy_swap-ZETA/ETH.ETH', # Свап Eddy Finance ZETA/ETH.ETH
    'eddy_swap-ZETA/BTC.BTC', # Свап Eddy Finance ZETA/BTC.BTC
    'izumi_liquidity-ZETA/BNB.BSC', # Добавить iZUMi ликвидность ZETA/BNB.BSC
    'izumi_liquidity-ZETA/ETH.ETH', # Добавить iZUMi ликвидность ZETA/ETH.ETH
    'izumi_liquidity-ZETA/BTC.BTC', # Добавить iZUMi ликвидность ZETA/BTC.BTC
    'mint_stzeta', # Минт $stZETA
    'claim', # Клейм поинтов
    'withdraw', # Вывод на адрес для депозита
]

# Настройки маршрутов
MIN_WALLET_BALANCE: float = 0.001 # Минимальный баланс кошелька в $ZETA, если баланс меньше то будет выводить с ОКХ сумму AMOUNT_TO_WITHDRAW
TRANSFER_AMOUNT: tuple[float, float] = (0.000001, 0.00001) # Мин, Макс сумма перевода самому себе в $ZETA
IZUMI_SWAP_AMOUNT: tuple[float, float] = (0.0001, 0.001) # Мин, Макс сумма свапа на iZUMi в $ZETA
EDDY_SWAP_AMOUNT: tuple[float, float] = (5.1, 5.5) # Мин, Макс сумма свапа на Eddy Finance в $USD (минимум 5$)
STZETA_MINT_AMOUNT: tuple[float, float] = (0.00001, 0.0001) # Мин, Макс сумма минта $stZETA
AMOUNT_TO_SAVE: tuple[float, float] = (0.02, 0.03) # Мин, Макс сумма для сохранения на кошельке в $ZETA
AMOUNT_TO_WITHDRAW: tuple[float, float] = (2, 2.2) # Мин, Макс сумма для вывода с ОКХ (минимум 2 $ZETA)

# Прочее
RPC: str = 'https://zetachain-evm.blockpi.network/v1/rpc/public'
EXPLORER: str = 'https://zetachain.blockscout.com/tx/'
REF_LINK: str = 'https://hub.zetachain.com/xp?code=YWRkcmVzcz0weGZjQUM1NGQ4QTc3NGM3OTAwOTJBNzJmNDFkYkYxOTFDODUzOGRCOUEmZXhwaXJhdGlvbj0xNzEyNDAxMDU0JnI9MHhlN2Y2Nzc4NjhhOGVmZmRhMGU2NWUzMDdiNjc2MmQ4YWE2MGQ5YzQ0YzI4ODM1ZTE0MTNiNjg5Y2YyNWNlMGM1JnM9MHg2NTFlNmM2Nzc4YzI5ZWMxMWRiYzk5NTkwMGExNTMzMGNmZTA3YWZiMWUyMGU0ZWE5MTg3MDFiNzIwMTk5ZjQ3JnY9Mjg%3D'

# OKX API (keep it secret)
OKX_API_KEY: str = ''
OKX_API_SECRET: str = ''
OKX_PASSPHRASE: str = ''

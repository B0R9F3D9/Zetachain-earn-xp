import json

with open("data/accounts.txt", "r") as file:
    ACCOUNTS = [x.strip() for x in file.readlines()]

with open('data/proxies.txt', 'r') as file:
    PROXIES = {i: x.strip() for i, x in enumerate(file.readlines(), 1)}

with open('data/deposit_addresses.txt', 'r') as file:
    WITHDRAW_ADDRESSES = {i: x.strip() for i, x in enumerate(file.readlines(), 1)}

with open('data/abi/erc20.json', 'r') as file:
    ERC20_ABI = json.load(file)

with open('data/abi/izumi_quoter.json', 'r') as file:
    IZUMI_QUOTER_ABI = json.load(file)

with open('data/abi/izumi_router.json', 'r') as file:
    IZUMI_ROUTER_ABI = json.load(file)

with open('data/abi/zetahub.json', 'r') as file:
    ZETAHUB_ABI = json.load(file)

TOKENS = {
    'ZETA': '0x5F0b1a82749cb4E2278EC87F8BF6B618dC71a8bf',
    'wZETA': '0x5F0b1a82749cb4E2278EC87F8BF6B618dC71a8bf',
    'BNB.BSC': '0x48f80608B672DC30DC7e3dbBd0343c5F02C738Eb',
    'ETH.ETH': '0x91d4f0d54090df2d81e834c3c8ce71c6c865e79f000bb8d97b1de3619ed2c6beb3860147e30ca8a7dc9891',
    'BTC.BTC': '0x7c8dda80bbbe1254a7aacf3219ebe1481c6e01d70027105f0b1a82749cb4e2278ec87f8bf6b618dc71a8bf00271013a0c5930c028511dc02665e7285134b6d11a5f4',
}

CONTRACTS = {
    'enroll': '0x3C85e0cA1001F085A3e58d55A0D76E2E8B0A33f9',
    'izumi_quoter': '0x8Afb66B7ffA1936ec5914c7089D50542520208b8',
    'izumi_router': '0x34bc1b87f60e0a30c0e24FD7Abada70436c71406',
    'zetahub': '0x2ca7d64A7EFE2D62A725E2B35Cf7230D6677FfEe',
}

TASKS_NAMES = {
    'WALLET_VERIFY': 'ВЕРИФ',
    'WALLET_VERIFY_BY_INVITE': 'РЕФ',
    'SEND_ZETA': 'ZETA->',
    'RECEIVE_ZETA': '->ZETA',
    'RECEIVE_BNB': 'BNB',
    'RECEIVE_BTC': 'BTC',
    'RECEIVE_ETH': 'ETH',
    'POOL_DEPOSIT_ANY_POOL': 'ПУЛ',
}

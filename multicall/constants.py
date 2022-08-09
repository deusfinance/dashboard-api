from enum import IntEnum


class Network(IntEnum):
    Fantom = 250
    Polygon = 137
    Mainnet = 1
    Kovan = 42
    Rinkeby = 4
    Görli = 5
    xDai = 100


MULTICALL_ADDRESSES = {
    Network.Fantom: '0xb828C456600857abd4ed6C32FAcc607bD0464F4F',
    Network.Polygon: '0x11ce4B23bD875D7F5C6a31084f55fDe1e9A87507',
    Network.Mainnet: '0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441',
    Network.Kovan: '0x2cc8688C5f75E365aaEEb4ea8D6a480405A48D2A',
    Network.Rinkeby: '0x42Ad527de7d4e9d9d011aC45B31D8551f8Fe9821',
    Network.Görli: '0x77dCa2C955b15e9dE4dbBCf1246B4B85b651e50e',
    Network.xDai: '0xb5b692a88BDFc81ca69dcB1d924f59f0413A602a',
}

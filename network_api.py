from web3 import Web3, WebsocketProvider
from web3.middleware import geth_poa_middleware

from config import CHAINS, DEI_ABI, DEI_ADDRESS, DEUS_ADDRESS, DEUS_ABI, USDC_ADDRESSES, PAIRS, PAIR_ABI


class NetworkApi:

    def __init__(self, chain_id, dao_list, is_poa=False) -> None:
        self.chain_id = chain_id
        self.dao_list = dao_list.copy()
        self.rpc = CHAINS[chain_id][0]
        self.w3 = Web3(WebsocketProvider(self.rpc))
        if is_poa:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.dei_contract = self.w3.eth.contract(DEI_ADDRESS, abi=DEI_ABI)
        self.deus_contract = self.w3.eth.contract(DEUS_ADDRESS, abi=DEUS_ABI)

    def get_deus_price(self):
        deus_native = self.w3.eth.contract(PAIRS[self.chain_id]['deus-native'], abi=PAIR_ABI)
        usdc_native = self.w3.eth.contract(PAIRS[self.chain_id]['native-usdc'], abi=PAIR_ABI)
        if deus_native.functions.token0().call() == DEUS_ADDRESS:
            deus_reserve = deus_native.functions.getReserves().call()[0]
            native_reserve0 = deus_native.functions.getReserves().call()[1]
        else:
            deus_reserve = deus_native.functions.getReserves().call()[1]
            native_reserve0 = deus_native.functions.getReserves().call()[0]

        if usdc_native.functions.token0().call() == USDC_ADDRESSES[self.chain_id]:
            usdc_reserve = usdc_native.functions.getReserves().call()[0]
            native_reserve1 = usdc_native.functions.getReserves().call()[1]
        else:
            usdc_reserve = usdc_native.functions.getReserves().call()[1]
            native_reserve1 = usdc_native.functions.getReserves().call()[0]

        price = (native_reserve0 * usdc_reserve * 1e12) / (deus_reserve * native_reserve1)
        return price

    def get_native_price(self):
        usdc_native = self.w3.eth.contract(PAIRS[self.chain_id]['native-usdc'], abi=PAIR_ABI)
        if usdc_native.functions.token0().call() == USDC_ADDRESSES[self.chain_id]:
            usdc_reserve = usdc_native.functions.getReserves().call()[0]
            native_reserve = usdc_native.functions.getReserves().call()[1]
        else:
            usdc_reserve = usdc_native.functions.getReserves().call()[1]
            native_reserve = usdc_native.functions.getReserves().call()[0]

        price = (usdc_reserve * 1e12) / native_reserve
        return price

    def dei_total_supply(self):
        return self.dei_contract.functions.totalSupply().call()

    def dei_circulating_marketcap(self):
        marketcap = self.dei_total_supply()
        for address in self.dao_list:
            marketcap -= self.dei_contract.functions.balanceOf(Web3.toChecksumAddress(address)).call()
        return marketcap

    def dei_minted_events(self, from_block):
        latest_block = self.w3.eth.block_number
        result = []
        entities = []
        size = 10000
        for i in range(from_block, latest_block + 1, size):
            entities.extend(self.dei_contract.events.DEIMinted.createFilter(fromBlock=i,
                                                                            toBlock=i + size).get_all_entries())
        for ent in entities:
            result.append({
                'amount': str(ent.args.amount),
                'block': ent.blockNumber,
                'timestamp': self.w3.eth.get_block(ent.blockNumber).timestamp
            })
        return result

    def deus_total_supply(self):
        return self.deus_contract.functions.totalSupply().call()

    def deus_burned_events(self, from_block):
        latest_block = self.w3.eth.block_number
        result = []
        entities = []
        size = 10000
        for i in range(from_block, latest_block + 1, size):
            entities.extend(self.deus_contract.events.DEUSBurned.createFilter(fromBlock=i,
                                                                              toBlock=i + size).get_all_entries())
        for ent in entities:
            result.append({
                'amount': str(ent.args.amount),
                'block': ent.blockNumber,
                'timestamp': self.w3.eth.get_block(ent.blockNumber).timestamp
            })
        return result

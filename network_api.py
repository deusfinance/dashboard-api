from web3 import Web3, WebsocketProvider
from web3.middleware import geth_poa_middleware

from config import CHAINS, DEI_ABI, DEI_ADDRESS, DEUS_ADDRESS, DEUS_ABI


class NetworkApi:

    def __init__(self, chain_id, is_poa=False) -> None:
        self.rpc = CHAINS[chain_id][0]
        self.w3 = Web3(WebsocketProvider(self.rpc))
        if is_poa:
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.dei_contract = self.w3.eth.contract(DEI_ADDRESS, abi=DEI_ABI)
        self.deus_contract = self.w3.eth.contract(DEUS_ADDRESS, abi=DEUS_ABI)

    def dei_total_supply(self):
        return self.dei_contract.functions.totalSupply().call()

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

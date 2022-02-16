from web3 import Web3, WebsocketProvider

from config import CHAINS, DEI_ABI, DEI_ADDRESS, DEUS_ADDRESS, DEUS_ABI

class NetworkApi:
    
    def __init__(self, chain_id) -> None:
        self.rpc = CHAINS[chain_id]   
        self.w3 = Web3(WebsocketProvider(self.rpc)) 
        self.dei_contract = self.w3.eth.contract(DEI_ADDRESS, abi=DEI_ABI)
        self.deus_contract = self.w3.eth.contract(DEUS_ADDRESS, abi=DEUS_ABI)

   
    def dei_total_supply(self):
        return self.dei_contract.functions.totalSupply().call()


    def dei_minted_events(self, from_block):
        result = []
        entities = self.dei_contract.events.DEIMinted.createFilter(fromBlock=from_block).get_all_entries()
        for ent in entities:
            result.append({
                'amount': ent.args.amount,
                'block': ent.blockNumber,
                'timestamp': self.w3.eth.get_block(ent.blockNumber).timestamp
            })
        return result


    def deus_total_supply(self):
        return self.deus_contract.functions.totalSupply().call()

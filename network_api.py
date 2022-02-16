from itertools import chain
from web3 import Web3, HTTPProvider, WebsocketProvider

from config import CHAINS, DEI_ABI, DEI_ADDRESS, DEUS_ADDRESS

class NetworkApi:
    
    def __init__(self, chain_id) -> None:
        self.rpc = CHAINS[chain_id]   
        self.w3 = Web3(WebsocketProvider(self.rpc)) 
        self.dei_contract = self.w3.eth.contract(DEI_ADDRESS, abi=DEI_ABI)
        # self.deus_contract = self.w3.eth.contract(DEUS_ADDRESS, abi=DEI_ABI)
        # self.contract.events.DEIMinted.createFilter()

    def dei_total_supply(self):
        return self.dei_contract.functions.totalSupply().call()
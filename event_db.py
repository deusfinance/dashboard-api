from typing import List
from config import CHAINS
from network_api import NetworkApi
import time 
from pymongo import MongoClient, DESCENDING

mongo_client = MongoClient('localhost', 27017)
database_name = 'statistics'

class EventDB:
    def __init__(self, db_name):
        self.db = mongo_client[db_name]
        self.networks = dict()
        for chain_id in CHAINS:
            self.networks[chain_id] = NetworkApi(chain_id)

    def dei_total_supply(self):
        total_supply = sum([self.networks[chain_id].dei_total_supply() for chain_id in self.networks])
        self.insert(
            table_name='dei_total_supply',
            documnts=[
                {
                    'timestamp': int(time.time()),
                    'total_supply': str(total_supply)
                }
            ]
        )


    def insert(self, table_name: str, documnts: List[dict]):
        if documnts:
            self.db[table_name].insert_many(documnts)

   
    def dei_minted_events(self):
        for chain_id, network in self.networks.items():
            last_item = self.db[f'minted_dei_{chain_id}'].find_one(sort=[( 'block', DESCENDING )])
            if not last_item:
                last_week = int(time.time()) - 7 * 24 * 60 * 60
                last_block = network.w3.eth.block_number()
                while network.w3.eth.get_block(last_block).timestamp >= last_week:
                    last_block -= 1000
            else:
                last_block = last_item['block']
            events = network.dei_minted_events(last_block)
            self.insert(f'minted_dei_{chain_id}', events)


    def deus_total_supply(self):
        total_supply = sum([self.networks[chain_id].deus_total_supply() for chain_id in self.networks])
        self.insert(
            table_name='deus_total_supply',
            documnts=[
                {
                    'timestamp': int(time.time()),
                    'total_supply': str(total_supply)
                }
            ]
        )

if __name__ == '__main__':
    e = EventDB(database_name)
    e.dei_minted_events()


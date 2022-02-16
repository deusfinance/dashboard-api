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
        for chain_id, value in CHAINS.items():
            self.networks[chain_id] = NetworkApi(chain_id, value[1])

    def dei_total_supply(self):
        total_supply = sum(self.networks[chain_id].dei_total_supply() for chain_id in self.networks)
        self.insert(
            table_name='dei_total_supply',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'total_supply': str(total_supply)
                }
            ]
        )

    def dei_circulating_marketcap(self):
        marketcap = sum(self.networks[chain_id].dei_circulating_marketcap() for chain_id in self.networks)
        self.insert(
            table_name='dei_circulating_marketcap',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'marketcap': str(marketcap)
                }
            ]
        )

    def get_dei_total_supply(self):
        return self.db['dei_total_supply'].find_one(sort=[('timestamp', DESCENDING)])['total_supply']

    def get_dei_circulating_marketcap(self):
        return self.db['dei_circulating_marketcap'].find_one(sort=[('timestamp', DESCENDING)])['marketcap']

    def insert(self, table_name: str, documents: List[dict]):
        if documents:
            self.db[table_name].insert_many(documents)

    def get_last_week_minted_dei(self):
        last_week = int(time.time()) - 7 * 24 * 60 * 60
        result = 0
        for chain_id, network in self.networks.items():
            chain_amount = 0
            for item in self.db[f'minted_dei_{chain_id}'].find(sort=[('timestamp', DESCENDING)]):
                if item['timestamp'] < last_week:
                    break
                chain_amount += int(item['amount'])
            print(chain_id, chain_amount * 1e-18, sep='\t')
            result += chain_amount
        return result

    def dei_minted_events(self):
        for chain_id, network in self.networks.items():
            last_item = self.db[f'minted_dei_{chain_id}'].find_one(sort=[('block', DESCENDING)])
            if not last_item:
                last_week = int(time.time()) - 7 * 24 * 60 * 60
                last_block = network.w3.eth.block_number
                while network.w3.eth.get_block(last_block).timestamp >= last_week:
                    print(last_block)
                    last_block -= 100000
            else:
                last_block = last_item['block']
            events = network.dei_minted_events(last_block + 1)
            print(events)
            self.insert(f'minted_dei_{chain_id}', events)

    def deus_total_supply(self):
        total_supply = sum([self.networks[chain_id].deus_total_supply() for chain_id in self.networks])
        self.insert(
            table_name='deus_total_supply',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'total_supply': str(total_supply)
                }
            ]
        )

    def deus_burned_events(self):
        for chain_id, network in self.networks.items():
            last_item = self.db[f'burned_deus_{chain_id}'].find_one(sort=[('block', DESCENDING)])
            if not last_item:
                last_week = int(time.time()) - 7 * 24 * 60 * 60
                last_block = network.w3.eth.block_number
                while network.w3.eth.get_block(last_block).timestamp >= last_week:
                    last_block -= 1000
            else:
                last_block = last_item['block']
            events = network.deus_burned_events(last_block)
            self.insert(f'burned_deus_{chain_id}', events)


if __name__ == '__main__':
    e = EventDB(database_name)
    e.deus_burned_events()

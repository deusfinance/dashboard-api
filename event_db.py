import sys
import traceback
from typing import List
from config import CONFIG
from network_api import NetworkApi
import time
from pymongo import MongoClient, DESCENDING, ASCENDING

from telegram_sender import sender

mongo_client = MongoClient('localhost', 27017)


def error_handler(func):
    def wrapped_func(*args, **kwargs):
        try:
            print(func.__name__, 'called')
            result = func(*args, **kwargs)
            print(func.__name__, 'updated')
        except Exception as ex:
            print('Error:', ex)
            print(traceback.format_exc(), file=sys.stderr)
            try:
                sender.send_message(f"Error in Updating statistics db:\n{ex}", ["notification"])
            except:
                pass
            return
        return result

    wrapped_func.__name__ = func.__name__
    return wrapped_func


class EventDB:
    def __init__(self, db_name):
        self.db = mongo_client[db_name]
        self.networks = dict()
        for chain_id, value in CONFIG.items():
            self.networks[chain_id] = NetworkApi(
                rpc=value['rpc'],
                chain_id=chain_id,
                source_price_chain=value['source_price_chain'],
                dei_ignore_list=value['dei_ignore_list'],
                deus_ignore_list=value['deus_ignore_list'],
                usdc_address=value['usdc_address'],
                pairs=value['pairs'],
                stakings=value['stakings'],
                path_to_usdc=value['path_to_usdc'],
                is_poa=value['is_poa'],
            )

    def insert(self, table_name: str, documents: List[dict]):
        if documents:
            self.db[table_name].insert_many(documents)

    @error_handler
    def dei_total_supply(self):
        total_supply = sum(self.networks[chain_id].dei_total_supply() for chain_id in self.networks)
        self.insert(
            table_name='dei_total_supply',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'total_supply': str(int(total_supply))
                }
            ]
        )

    @error_handler
    def dei_circulating_marketcap(self):
        marketcap = sum(self.networks[chain_id].dei_circulating_marketcap() for chain_id in self.networks)
        self.insert(
            table_name='dei_circulating_marketcap',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'marketcap': str(int(marketcap))
                }
            ]
        )

    @error_handler
    def deus_total_supply(self):
        total_supply = sum(self.networks[chain_id].deus_total_supply() for chain_id in self.networks)
        self.insert(
            table_name='deus_total_supply',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'total_supply': str(int(total_supply))
                }
            ]
        )

    @error_handler
    def deus_circulating_marketcap(self):
        total_supply = sum(self.networks[chain_id].deus_circulating_total_supply() for chain_id in self.networks)
        price = self.networks[250].get_source_deus_price()
        self.insert(
            table_name='deus_circulating_marketcap',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'marketcap': str(int(total_supply * price))
                }
            ]
        )

    @error_handler
    def dei_minted_events(self):
        for chain_id, network in self.networks.items():
            last_item = self.db[f'minted_dei_{chain_id}'].find_one(sort=[('block', DESCENDING)])
            if not last_item:
                last_week = int(time.time()) - 7 * 24 * 60 * 60
                last_block = network.w3.eth.block_number
                while network.w3.eth.get_block(last_block).timestamp >= last_week:
                    last_block -= 100000
            else:
                last_block = last_item['block']
            events = network.dei_minted_events(last_block + 1)
            self.insert(f'minted_dei_{chain_id}', events)

    @error_handler
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

    @error_handler
    def staked_deus_liquidity(self):
        liquidity = sum(self.networks[chain_id].staked_deus_liquidity() for chain_id in self.networks)
        self.insert(
            table_name='staked_deus_liquidity',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'liquidity': str(int(liquidity))
                }
            ]
        )

    @error_handler
    def staked_dei_liquidity(self):
        liquidity = sum(self.networks[chain_id].staked_dei_liquidity() for chain_id in self.networks)
        self.insert(
            table_name='staked_dei_liquidity',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'liquidity': str(int(liquidity))
                }
            ]
        )

    @error_handler
    def deus_dex_liquidity(self):
        liquidity = sum(self.networks[chain_id].deus_dex_liquidity() for chain_id in self.networks)
        self.insert(
            table_name='deus_dex_liquidity',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'liquidity': str(int(liquidity))
                }
            ]
        )

    @error_handler
    def dei_dex_liquidity(self):
        liquidity = sum(self.networks[chain_id].dei_dex_liquidity() for chain_id in self.networks)
        self.insert(
            table_name='dei_dex_liquidity',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'liquidity': str(int(liquidity))
                }
            ]
        )

    @error_handler
    def deus_emissions(self):
        current_block = self.networks[250].w3.eth.block_number
        last_item = self.db['deus_emissions'].find_one(sort=[('timestamp', DESCENDING)])
        if not last_item:
            last_block = current_block - 1
        last_block = last_item['block']
        current_block = self.networks[250].w3.eth.block_number
        emissions = self.networks[250].deus_emissions()
        emissions_value = emissions * (current_block - last_block)
        self.insert(
            table_name='deus_emissions',
            documents=[
                {
                    'timestamp': int(time.time()),
                    'block': current_block,
                    'emissions': str(int(emissions)),
                    'emissions_value': str(int(emissions_value))
                }
            ]
        )

    def get_dei_total_supply(self):
        return self.db['dei_total_supply'].find_one(sort=[('timestamp', DESCENDING)])['total_supply']

    def get_dei_circulating_marketcap(self):
        return self.db['dei_circulating_marketcap'].find_one(sort=[('timestamp', DESCENDING)])['marketcap']

    def get_minted_dei(self, interval):
        from_time = int(time.time()) - interval
        result = 0
        for chain_id, network in self.networks.items():
            chain_amount = 0
            for item in self.db[f'minted_dei_{chain_id}'].find(sort=[('timestamp', DESCENDING)]):
                if item['timestamp'] < from_time:
                    break
                chain_amount += int(item['amount'])
            result += chain_amount
        return str(result)

    def get_last_week_minted_dei(self):
        return self.get_minted_dei(7 * 24 * 60 * 60)

    def get_deus_total_supply(self):
        return self.db['deus_total_supply'].find_one(sort=[('timestamp', DESCENDING)])['total_supply']

    def get_deus_marketcap(self):
        total_supply = int(self.get_deus_total_supply())
        price = self.networks[250].get_source_deus_price()
        return str(int(total_supply * price))

    def get_deus_circulating_marketcap(self):
        marketcap = self.db['deus_circulating_marketcap'].find_one(sort=[('timestamp', DESCENDING)])['marketcap']
        return str(int(int(marketcap)))

    def get_staked_deus_liquidity(self):
        return self.db['staked_deus_liquidity'].find_one(sort=[('timestamp', DESCENDING)])['liquidity']

    def get_staked_dei_liquidity(self):
        return self.db['staked_dei_liquidity'].find_one(sort=[('timestamp', DESCENDING)])['liquidity']

    def get_deus_dex_liquidity(self):
        return self.db['deus_dex_liquidity'].find_one(sort=[('timestamp', DESCENDING)])['liquidity']

    def get_dei_dex_liquidity(self):
        return self.db['dei_dex_liquidity'].find_one(sort=[('timestamp', DESCENDING)])['liquidity']

    def get_deus_burned_events(self, interval):
        from_time = int(time.time()) - interval
        result = 0
        for chain_id, network in self.networks.items():
            chain_amount = 0
            for item in self.db[f'burned_deus_{chain_id}'].find(sort=[('timestamp', DESCENDING)]):
                if item['timestamp'] < from_time:
                    break
                chain_amount += int(item['amount'])
            result += chain_amount
        return str(result)

    def get_deus_emissions(self, interval):
        from_time = int(time.time()) - interval
        current_block = self.networks[250].w3.eth.block_number
        last_week_record = self.db['deus_emissions'].find_one({'timestamp': {'$lte': from_time}},
                                                              sort=[('timestamp', DESCENDING)])
        if not last_week_record:
            emissions = sum(int(r['emissions_value']) for r in self.db['deus_emissions'].find())
            first_item = self.db['deus_emissions'].find_one(sort=[('timestamp', ASCENDING)])
            emissions += ((first_item['timestamp'] - from_time) / (int(time.time()) - first_item['timestamp'])) * (current_block - first_item['block']) * int(first_item['emissions'])
        else:
            emissions = sum(int(r['emissions_value']) for r in self.db['deus_emissions'].find({'timestamp': {'$lte': from_time}}, sort=[('timestamp', DESCENDING)]))
        return emissions

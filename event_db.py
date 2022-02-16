from config import CHAINS
from network_api import NetworkApi


class EventDB:
    def __init__(self) -> None:
        self.networks = dict()
        for chain_id in CHAINS:
            self.networks[chain_id] = NetworkApi(chain_id)

    def dei_total_supply(self):
        dei_total_supply = 0 
        for chain_id, network in self.networks.items():
            dei_total_supply += network.dei_total_supply()
        print(dei_total_supply)
        # add to db

if __name__ == '__main__':
    e = EventDB()
    e.dei_total_supply()


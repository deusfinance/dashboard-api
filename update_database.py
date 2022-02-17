import time

from event_db import EventDB
from config import DEUS_ADDRESS


def main():
    db = EventDB('statistics')
    db.deus_dex_liquidity()
    db.dei_dex_liquidity()
    db.staked_deus_liquidity()
    db.staked_dei_liquidity()
    db.dei_total_supply()
    db.deus_total_supply()
    db.deus_circulating_marketcap()
    db.dei_circulating_marketcap()
    db.deus_burned_events()
    db.dei_minted_events()



if __name__ == '__main__':
    while True:
        try:
            print('\t\tstart: ', time.ctime())
            main()
            print('\t\tend: ', time.ctime())
        except KeyboardInterrupt:
            exit()
        except Exception as ex:
            print(ex)
        time.sleep(30)

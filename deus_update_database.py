import time

from event_db import EventDB


def main():
    db = EventDB('statistics')
    db.deus_price()
    db.deus_emissions()
    db.deus_dex_liquidity()
    db.staked_deus_liquidity()
    db.deus_total_supply()
    db.deus_circulating_supply()
    db.deus_circulating_marketcap()


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
        time.sleep(1*60)

import time
from event_db import EventDB

db = EventDB('statistics')


def dei_2step():
    db.dei_dex_liquidity()
    db.staked_dei_liquidity()
    db.dei_total_supply()
    db.dei_circulating_marketcap()
    db.dei_redeem_lower_bound()
    db.dei_circulating_supply()


def deus_2step():
    db.deus_price()
    db.deus_emissions()
    db.deus_dex_liquidity()
    db.staked_deus_liquidity()
    db.deus_total_supply()
    db.deus_circulating_supply()
    db.deus_circulating_marketcap()


def dei_20step():
    db.dei_minted_events()


def deus_20step():
    db.deus_burned_events()


if __name__ == '__main__':
    counter = 0
    while True:
        try:
            print('\t\tstart: ', time.ctime())

            if counter % 2 == 0:
                dei_2step()
                deus_2step()
            if counter % 20 == 0:
                dei_20step()
                deus_20step()

            print('\t\tend: ', time.ctime())
        except KeyboardInterrupt:
            exit()
        except Exception as ex:
            print(ex)
        counter += 1
        time.sleep(10)

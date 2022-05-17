import time

from event_db import EventDB


def main():
    db = EventDB('statistics')
    db.dei_dex_liquidity()
    db.staked_dei_liquidity()
    db.dei_total_supply()
    db.dei_circulating_marketcap()
    db.dei_redeem_lower_bound()
    db.dei_circulating_supply()


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

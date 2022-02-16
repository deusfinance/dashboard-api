import time

from event_db import EventDB


def main():
    db = EventDB('statistics')
    db.dei_total_supply()
    db.dei_circulating_marketcap()
    db.deus_total_supply()
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
        time.sleep(5 * 60)

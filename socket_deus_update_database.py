import time

from event_db import EventDB


def main():
    db = EventDB('statistics')
    db.deus_burned_events()


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
        time.sleep(2*60)

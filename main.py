from flask import Flask, jsonify, request
from event_db import EventDB

app = Flask(__name__)
event_db = EventDB('statistics')


def exception_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            print(ex)
            return jsonify(status='ERROR', message=str(ex)), 400

    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/deus/price', methods=['GET'])
@exception_decorator
def get_deus_price():
    return event_db.get_deus_price()


@app.route('/deus/total-supply', methods=['GET'])
@exception_decorator
def get_deus_total_supply():
    return event_db.get_deus_total_supply()


@app.route('/deus/circulating-supply', methods=['GET'])
@exception_decorator
def get_deus_circulating_supply():
    return event_db.get_deus_circulating_supply()


@app.route('/deus/marketcap', methods=['GET'])
@exception_decorator
def get_deus_marketcap():
    return event_db.get_deus_marketcap()


@app.route('/deus/circulating-marketcap', methods=['GET'])
@exception_decorator
def get_deus_circulating_marketcap():
    return event_db.get_deus_circulating_marketcap()


@app.route('/deus/staked-liquidity', methods=['GET'])
@exception_decorator
def get_staked_deus_liquidity():
    return event_db.get_staked_deus_liquidity()


@app.route('/deus/dex-liquidity', methods=['GET'])
@exception_decorator
def get_deus_dex_liquidity():
    return event_db.get_deus_dex_liquidity()


@app.route('/deus/emissions', methods=['GET'])
@exception_decorator
def get_deus_emissions():
    return str(event_db.get_deus_emissions(7 * 24 * 60 * 60))


@app.route('/deus/burned-amount/<interval>', methods=['GET'])
@exception_decorator
def get_deus_burned_events(interval):
    return str(event_db.get_deus_burned_events(int(interval)))


@app.route('/dei/minted-amount/<interval>', methods=['GET'])
@exception_decorator
def get_minted_dei(interval):
    return str(event_db.get_minted_dei(int(interval)))


@app.route('/dei/total-supply', methods=['GET'])
@exception_decorator
def get_dei_total_supply():
    return event_db.get_dei_total_supply()


@app.route('/dei/circulating-supply', methods=['GET'])
@exception_decorator
def get_dei_circulating_supply():
    return event_db.get_dei_circulating_supply()

@app.route('/dei/redeem-lower-bound', methods=['GET'])
@exception_decorator
def get_dei_redeem_lower_bound():
    return event_db.get_dei_redeem_lower_bound()

@app.route('/dei/marketcap', methods=['GET'])
@exception_decorator
def get_dei_circulating_marketcap():
    return event_db.get_dei_circulating_marketcap()


@app.route('/dei/staked-liquidity', methods=['GET'])
@exception_decorator
def get_staked_dei_liquidity():
    return event_db.get_staked_dei_liquidity()


@app.route('/dei/dex-liquidity', methods=['GET'])
@exception_decorator
def get_dei_dex_liquidity():
    return event_db.get_dei_dex_liquidity()


@app.route('/info', methods=['GET'])
# @exception_decorator
def get_info():
    return {
        'deus_price': event_db.get_deus_price(),
        'deus_total_supply': event_db.get_deus_total_supply(),
        'deus_circulating_supply': event_db.get_deus_circulating_supply(),
        'deus_marketcap': event_db.get_deus_circulating_marketcap(),
        'deus_fully_diluted_valuation': event_db.get_deus_marketcap(),
        'deus_emissions': event_db.get_deus_emissions(7 * 24 * 60 * 60),
        'staked_deus_liquidity': event_db.get_staked_deus_liquidity(),
        'deus_dex_liquidity': event_db.get_deus_dex_liquidity(),
        'deus_burned_events': event_db.get_deus_burned_events(7 * 24 * 60 * 60),
        'minted_dei': event_db.get_minted_dei(7 * 24 * 60 * 60),
        'dei_total_supply': event_db.get_dei_total_supply(),
        'dei_marketcap': event_db.get_dei_circulating_marketcap(),
        'staked_dei_liquidity': event_db.get_staked_dei_liquidity(),
        'dei_dex_liquidity': event_db.get_dei_dex_liquidity(),
        'dei_redeem_lower_bound': event_db.get_dei_redeem_lower_bound(),
        'dei_circulating_supply': event_db.get_dei_circulating_supply()
    }


if __name__ == "__main__":
    app.run(port=3010, host='0.0.0.0', debug=True)

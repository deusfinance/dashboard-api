import requests

from web3 import HTTPProvider, Web3
from config import BOT_TOKEN, CONFIG, DEUS_ADDRESS


def send_telegram(message, chat_id):
    data = {
        'chat_id': chat_id,
        'text': message,
        'disable_web_page_preview': True
    }
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'
    requests.post(url=url, data=data)


def get_deus_price(network):
    w3 = Web3(HTTPProvider(CONFIG[250]['rpc_http'])[0])
    return network.get_token_price(DEUS_ADDRESS,
                                   pair_addresses=CONFIG[250]['path_to_usdc'][DEUS_ADDRESS], w3=w3)

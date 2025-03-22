# market.py
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI()

def getPrice(coin):
    price = cg.get_price(ids=str(coin), vs_currencies='usd')
    return price['bitcoin']['usd']


def changesof24h(coin):
    history = cg.get_price(coin, include_24hr_change=True, vs_currencies='usd')
    return history['bitcoin']['usd_24h_change']
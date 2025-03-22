from market import getPrice, changesof24h


def makeReady(coin):
    getprices = getPrice(coin)
    getChanges = changesof24h(coin)
    return getprices , getChanges
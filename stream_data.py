
from binance.client import Client
from binance.websockets import BinanceSocketManager
from futures_websocket import FuturesWebsockets
from futures_websocket import FuturesClient
from datetime import datetime
import time

proxies = {
    'https': 'http://nadia:BFwpjkRyZp7ASKsk@137.74.153.120:8999',
    'http': 'http://nadia:BFwpjkRyZp7ASKsk@137.74.153.120:8999'
}
# init
api_key = "B0ZudxaRUw2p5yUI01ja1DCEwA14dCpDtR4EMYsMAYbyVJUmM928uxpCLVRDS2No"
api_secret = "DLgAg9ENXVQCbpWV2Zd2erGlXDJJthTCD1dkUJkMREP8OptRz6TTfrFnAYpHYCKu"
client = FuturesClient(api_key, api_secret, {
    'proxies': proxies, "verify": False, "timeout": 20})
bm = FuturesWebsockets(client)

_symbol = None
_activate_price = None
_stop_limit_price = None
_take_profit_price = None
_quantity = None
_stop_limit_order = None
_take_profit_order = None


def handle_message(msg):
    msg = msg['data']
    if msg['e'] == 'error':
        print(msg['m'])

    else:
        # Bitcoins exchanged - This time converting the strings to floats.
        bitcoins_exchanged = float(msg['p']) * float(msg['q'])

        # Make time pretty
        timestamp = msg['T'] / 1000
        timestamp = datetime.fromtimestamp(
            timestamp).strftime('%Y-%m-%d %H:%M:%S')

        # Buy or sell?
        if msg['m'] == True:
            event_side = 'SELL'
        else:
            event_side = 'BUY '

        # Print this amount
        print("{} - {} - {} - Price: {} - Qty: {} BTC Qty: {}".format(timestamp,
                                                                      event_side,
                                                                      msg['s'],
                                                                      msg['p'],
                                                                      msg['q'],
                                                                      bitcoins_exchanged))


def sl_tp_order(symbol, quantity, activate_price, stop_limit_price, take_profit_price):
    _symbol = symbol
    _activate_price = activate_price
    _quantity = quantity
    _stop_limit_price = stop_limit_price
    _take_profit_price = take_profit_price
    # start any sockets here, i.e a trade socket
    conn_key = bm.start_aggtrade_futures_socket(_symbol, handle_message)
    # conn_key = bm.start_futures_user_socket(handle_message)

    # then start the socket manager
    bm.start()

from binance.client import Client
from binance.websockets import BinanceSocketManager
from futures_websocket import FuturesWebsockets
from futures_websocket import FuturesClient
from datetime import datetime
import time

proxies = {
    "https": "http://nadia:BFwpjkRyZp7ASKsk@137.74.153.120:8999",
    "http": "http://nadia:BFwpjkRyZp7ASKsk@137.74.153.120:8999",
}

# key = tij1weHgbtBPpGe80FzwYqUs0fFwv5ZDdOe0wGK2TS63xk24TFiNWQNLRWYPgT7H
# secret = W9130sdA9441laN45NaSEOS0pW6VYb396Qr3t99nM9Tcs6RUds9MZ66TBkmtBOrG
# init
api_key = "B0ZudxaRUw2p5yUI01ja1DCEwA14dCpDtR4EMYsMAYbyVJUmM928uxpCLVRDS2No"
api_secret = "DLgAg9ENXVQCbpWV2Zd2erGlXDJJthTCD1dkUJkMREP8OptRz6TTfrFnAYpHYCKu"
client = FuturesClient(
    api_key, api_secret, {"proxies": proxies, "verify": False, "timeout": 20}
)


class FuturesSlTpOrder:
    def __init__(
        self,
        client,
        symbol,
        activate_price,
        stop_limit_price,
        take_profit_price,
        quantity,
    ):
        self._client = client
        self._symbol = symbol
        self._activate_price = activate_price
        self._stop_limit_price = stop_limit_price
        self._take_profit_price = take_profit_price
        self._quantity = quantity
        self._stop_limit_order = None
        self._take_profit_order = None
        self._ws = FuturesWebsockets(client)

    def handle_message(self, msg):
        msg = msg["data"]
        if msg["e"] == "error":
            print(msg["m"])

        else:
            # Bitcoins exchanged - This time converting the strings to floats.
            bitcoins_exchanged = float(msg["p"]) * float(msg["q"])

            # Make time pretty
            timestamp = msg["T"] / 1000
            timestamp = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

            # Buy or sell?
            if msg["m"] == True:
                event_side = "SELL"
            else:
                event_side = "BUY "

            # Print this amount
            print(
                "{} - {} - {} - Price: {} - Qty: {} BTC Qty: {}".format(
                    timestamp,
                    event_side,
                    msg["s"],
                    msg["p"],
                    msg["q"],
                    bitcoins_exchanged,
                )
            )
            if self._activate_price and msg["p"] == self._activate_price:
                self.send_sl_tp_orders()
            if msg["p"] == self._stop_limit_price:
                self.cancel_order(self._take_profit_order["orderId"])
            if msg["p"] == self._take_profit_price:
                self.cancel_order(self._stop_limit_order["orderId"])

    def send_sl_tp_order(self):
        # start any sockets here, i.e a trade socket
        conn_key = self._ws.start_aggtrade_futures_socket(
            self._symbol, self.handle_message
        )
        # conn_key = bm.start_futures_user_socket(handle_message)

        # then start the socket manager
        self._ws.start()

    def send_sl_tp_orders(self):
        print("send Orders")
        self._stop_limit_order = client.futures_create_order(
            symbol=self._symbol,
            side="BUY",
            type="STOP_MARKET ",
            quantity=self._quantity,
            stopPrice=self._stop_limit_price,
        )
        self._take_profit_order = client.futures_create_order(
            symbol=self._symbol,
            side="BUY",
            type="TAKE_PROFIT ",
            quantity=self._quantity,
            stopPrice=self._take_profit_price,
        )

    def cancel_order(order_id):
        client.futures_cancel_order(order_id)
        print("cancel Order:", order_id)

from futures_websocket import FuturesWebsockets
from datetime import datetime
import time


class FuturesSlTpOrder:
    def __init__(
        self,
        client,
        symbol,
        activate_price,
        price,
        stop_limit_price,
        take_profit_price,
        quantity_in_usdt,
    ):
        self._client = client
        self._symbol = symbol
        self._activate_price = activate_price
        self._price = price
        self._stop_limit_price = stop_limit_price
        self._take_profit_price = take_profit_price
        self._quantity = self.calculate_quantity(quantity_in_usdt)
        self._stop_limit_order = None
        self._take_profit_order = None
        self._ws = FuturesWebsockets(self._client)

    def calculate_quantity(self,quantity_in_usdt):
        info = self._client.futures_exchange_info()
        symbols_n_precision={}
        for item in info['symbols']: 
            symbols_n_precision[item['symbol']] = item['quantityPrecision']
        precision = symbols_n_precision[self._symbol]
        return float(round(quantity_in_usdt / self._price, 3))

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
            if self._activate_price and int(float(msg["p"])) == self._activate_price:
                self.send_sl_tp_orders()

            if self._stop_limit_order and int(float(msg["p"])) <= self._stop_limit_price:
                self.cancel_sl_tp_order(self._take_profit_order["orderId"])

            if self._take_profit_order and int(float(msg["p"])) >= self._take_profit_price:
                self.cancel_sl_tp_order(self._stop_limit_order["orderId"])

    def start_order(self):
        # start any sockets here, i.e a trade socket
        orderId = "8389765497774189430"
        self.cancel_sl_tp_order(orderId)
        conn_key = self._ws.start_aggtrade_futures_socket(
            self._symbol, self.handle_message
        )
        # conn_key = bm.start_futures_user_socket(handle_message)

        # then start the socket manager
        self._ws.start()

    def cancel_order(self):
        self.cancel_sl_tp_order(self._take_profit_price["orderId"])
        self.cancel_sl_tp_order(self._stop_limit_order["orderId"])

    def send_sl_tp_orders(self):
        print("send Orders")
        self._client.futures_create_order(
            symbol=self._symbol,
            price=self._price,
            side="BUY",
            type="MARKET",
            quantity=self._quantity,
            timeInForce='GTC'
        )
        self._stop_limit_order = self._client.futures_create_order(
            symbol=self._symbol,
            price=self._price,
            side="SELL",
            type="STOP",
            quantity=self._quantity,
            stopPrice=self._stop_limit_price,
            timeInForce='GTC'
        )
        self._take_profit_order = self._client.futures_create_order(
            symbol=self._symbol,
            price=self._price,
            side="SELL",
            type="TAKE_PROFIT",
            quantity=self._quantity,
            stopPrice=self._take_profit_price,
            timeInForce='GTC'
        )

    def cancel_sl_tp_order(self, order_id):
        print("cancel Order:", order_id)
        self._client.futures_cancel_order(symbol=self._symbol, orderId=order_id)

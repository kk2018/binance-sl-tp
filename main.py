from futures_websocket import FuturesClient
from futures_websocket import FuturesWebsockets

from stream_data import FuturesSlTpOrder

proxies = {
    "https": "http://nadia:BFwpjkRyZp7ASKsk@137.74.153.120:8999",
    "http": "http://nadia:BFwpjkRyZp7ASKsk@137.74.153.120:8999",
}
# init
# tr.trade.team.5@gmail.com
api_key = "tij1weHgbtBPpGe80FzwYqUs0fFwv5ZDdOe0wGK2TS63xk24TFiNWQNLRWYPgT7H"
api_secret = "W9130sdA9441laN45NaSEOS0pW6VYb396Qr3t99nM9Tcs6RUds9MZ66TBkmtBOrG"

# rebinnaf@gmail.com
# api_key = "B0ZudxaRUw2p5yUI01ja1DCEwA14dCpDtR4EMYsMAYbyVJUmM928uxpCLVRDS2No"
# api_secret = "DLgAg9ENXVQCbpWV2Zd2erGlXDJJthTCD1dkUJkMREP8OptRz6TTfrFnAYpHYCKu"

def main():
    client = FuturesClient(
        api_key,
        api_secret,
        {"proxies": proxies, "verify": False, "timeout": 20},
    )

    print(client.futures_account_balance())

    order = FuturesSlTpOrder(
        client=client,
        symbol="BTCUSDT",
        activate_price=42800,
        take_profit_price=42810,
        stop_limit_price=42790,
        quantity_in_usdt=10,
    )

    order.start_order()

if __name__ == "__main__":
    main()

# coding=utf-8
import threading
from binance.client import Client
from binance.websockets import BinanceSocketManager


class FuturesClient(Client):
    def _request_futures_api(self, method, path, signed=False, **kwargs):
        uri = self._create_futures_api_uri(path)
        print("request to:", uri)

        return self._request(method, uri, signed, True, **kwargs)

    def futures_stream_get_listen_key(self):
        res = self._request_futures_api("post", "listenKey", signed=False, data={})
        return res["listenKey"]

    def futures_stream_keepalive(self, listenKey):
        params = {"listenKey": listenKey}
        return self._request_futures_api("put", "listenKey", signed=False, data=params)

    def futures_stream_close(self, listenKey):

        params = {"listenKey": listenKey}
        return self._request_futures_api(
            "delete", "listenKey", signed=False, data=params
        )


class FuturesWebsockets(BinanceSocketManager):
    STREAM_URL = "wss://stream.binance.com:9443/"
    FSTREAM_URL = "wss://fstream.binance.com/"
    VSTREAM_URL = "wss://vstream.binance.com/"
    VSTREAM_TESTNET_URL = "wss://testnetws.binanceops.com/"

    WEBSOCKET_DEPTH_5 = "5"
    WEBSOCKET_DEPTH_10 = "10"
    WEBSOCKET_DEPTH_20 = "20"

    DEFAULT_USER_TIMEOUT = 30 * 60  # 30 minutes

    def __init__(self, client, user_timeout=DEFAULT_USER_TIMEOUT):
        super().__init__(client, user_timeout)
        self._timers = {"user": None, "margin": None, "futures": None}
        self._listen_keys = {"user": None, "margin": None, "futures": None}
        self._account_callbacks = {"user": None, "margin": None, "futures": None}

    def start_futures_user_socket(self, callback):
        """Start a websocket for user data
        https://github.com/binance-exchange/binance-official-api-docs/blob/master/user-data-stream.md
        https://binance-docs.github.io/apidocs/spot/en/#listen-key-spot
        :param callback: callback function to handle messages
        :type callback: function
        :returns: connection key string if successful, False otherwise
        Message Format - see Binance API docs for all types
        """
        # Get the user listen key
        user_listen_key = self._client.futures_stream_get_listen_key()
        # and start the socket with this specific key
        return self._start_account_futures_socket("futures", user_listen_key, callback)

    def _start_account_futures_socket(self, socket_type, listen_key, callback):
        """Starts futures account socket"""
        self._check_account_socket_open(listen_key)
        self._listen_keys[socket_type] = listen_key
        self._account_callbacks[socket_type] = callback
        conn_key = self._start_futures_socket(listen_key, callback, "ws/")
        if conn_key:
            # start timer to keep socket alive
            self._start_socket_timer(socket_type)
        return conn_key

    def _keepalive_account_socket(self, socket_type):
        if socket_type == "user":
            callback = self._account_callbacks[socket_type]
            listen_key = self._client.stream_get_listen_key()
        elif socket_type == "margin":  # cross-margin
            listen_key_func = self._client.margin_stream_get_listen_key
            callback = self._account_callbacks[socket_type]
            listen_key = listen_key_func()
        elif socket_type == "futures":
            listen_key_func = self._client.futures_stream_get_listen_key
            callback = self._account_callbacks[socket_type]
            listen_key = self._client.margin_stream_get_listen_key()
            listen_key = listen_key_func()
        else:  # isolated margin
            listen_key_func = self._client.isolated_margin_stream_get_listen_key
            callback = self._account_callbacks.get(socket_type, None)
            listen_key = self._client.isolated_margin_stream_get_listen_key(
                socket_type
            )  # Passing symbol for isolated margin

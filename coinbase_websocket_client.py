import os
import json
import datetime
import logging
from decimal import Decimal

import websocket
from websocket import WebSocketApp
from dateutil.tz import tzlocal
from orderbook import OrderBook


class CoinbaseWebsocketClient:
    """Coinbase Pro Websocket API"""
    # max error count before close websocket
    MAX_ERROR_COUNT = 5

    # logging settings
    if os.path.exists("order_book.log"):
        os.remove("order_book.log")
    logging.basicConfig(filename='order_book.log', level=logging.INFO)

    def __init__(self, url=None, products=None, channels=None):
        self.url = "wss://ws-feed.exchange.coinbase.com" if not url else url
        self.product_ids = ["BTC-USD"] if not products else products
        self.channels = ["heartbeat", "full"] if not channels else channels
        self.heartbeat = datetime.datetime.now(tzlocal())
        self.error_count = 0
        self.ws = None
        self.sequence = None

        self.order_book = OrderBook()

    @staticmethod
    def _decimal_round(num, num_digits=8):
        """
        round the number to num_digits decimal places

        :param num: number
        :param num_digits: number of decimal places, either 2 or 8
        :return: rounded number

        """
        digit = "1.00000000" if num_digits == 8 else "1.00"
        return Decimal(num).quantize(Decimal(digit))

    def on_open(self, ws):
        """on open"""
        logging.info("Websocket connected")

        # subscribe
        self._subscribe(ws)

    def _subscribe(self, ws):
        """subscribe to the channels"""
        ws.send(
            json.dumps(
                {
                    "type": "subscribe",
                    "product_ids": self.product_ids,
                    "channels": self.channels,
                }
            )
        )
        logging.info(f"Subscribed to channels:{self.channels}")

    def on_message(self, ws, message: str):
        """
        on message

        :param ws: websocket
        :param message: incoming message

        """
        message = json.loads(message)

        # checking for sequence error
        self._check_sequence(ws, message)

        # processing message
        self._process_message(ws, message)

        self.order_book.print_price()

    def _check_sequence(self, ws, message: dict):
        """
        check if there is sequence error

        :param ws: websocket
        :param message: incoming json message

        """
        full_channel = {"open", "done", "match", "change", "activate", "received"}
        if message["type"] in full_channel:
            sequence = message["sequence"]
            if self.sequence is None:
                self.sequence = sequence
            elif sequence <= self.sequence:
                logging.warning(f"Sequence error: new sequence <= old sequence")
                return
            else:
                if sequence - self.sequence != 1:
                    self.on_error(ws, f"Sequence error: missing {sequence - self.sequence - 1} sequences")
                    return
                self.sequence = sequence

    def _process_message(self, ws, message: dict):
        """
        process incoming message

        :param ws: websocket
        :param message: message dict

        """
        if message["type"] == "heartbeat":
            # if heartbeat is not received for 5 seconds, close websocket
            if (datetime.datetime.now(tzlocal()) -
                    self.heartbeat).total_seconds() > 5:
                logging.warning("Websocket heartbeat timeout")
                self.close()
            self.heartbeat = datetime.datetime.now(tzlocal())
        elif message["type"] == "error":
            self.on_error(ws, message["message"])
        elif message["type"] == "open":
            side = "bid" if message["side"] == "buy" else "ask"
            self.order_book.insert_order(message["order_id"],
                                         self._decimal_round(message["remaining_size"]),
                                         self._decimal_round(message["price"], 2), side)
        elif message["type"] == "done":
            side = "bid" if message["side"] == "buy" else "ask"
            self.order_book.delete_order(message["order_id"], side)
        elif message["type"] == "change":
            side = "bid" if message["side"] == "buy" else "ask"
            if "new_price" in message:
                self.order_book.change_order_price(message["order_id"],
                                                   self._decimal_round(message["old_price"], 2),
                                                   self._decimal_round(message["new_price"], 2), side)
            if "new_size" in message and message["new_size"] != message["old_size"]:
                # string comparison, no need to worry about precision
                self.order_book.change_order_size(message["order_id"],
                                                  self._decimal_round(message["new_size"]), side)
        elif message["type"] == "match":
            order_id = message["maker_order_id"]
            side = "bid" if message["side"] == "sell" else "ask"
            self.order_book.match_order(order_id, self._decimal_round(message["size"]), side)

    def on_error(self, ws, error: str):
        """
        on error
        :param ws: websocket
        :param error: error message

        """
        logging.error(error)
        self.error_count += 1
        if self.error_count > self.MAX_ERROR_COUNT:
            logging.error("Max error count reached, close websocket")
            ws.close()

    def connect(self):
        """connect websocket"""
        websocket.setdefaulttimeout(5)
        self.ws = WebSocketApp(
            self.url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            keep_running=True,
        )
        self.ws.run_forever()

    def close(self):
        """close websocket"""
        if self.ws:
            self.ws.close()
            self.ws = None
            logging.info("Websocket closed")


if __name__ == "__main__":
    websocket_client = CoinbaseWebsocketClient()
    websocket_client.connect()

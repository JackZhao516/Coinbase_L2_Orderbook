import io
import json
import unittest.mock
from decimal import Decimal
from orderbook import OrderBook
from coinbase_websocket_client import CoinbaseWebsocketClient


class TestWebSocket(unittest.TestCase):
    def test_message(self):
        """
        test websocket message_process function
        """
        self.message_helper("test_message_1.json", "0.00989427@18882.20\n"
                                                   "----------------------\n"
                                                   "0.02684411@18878.53\n\n\n\n")

        self.message_helper("test_message_2.json", "0.61228293@18895.24\n"
                                                   "0.10000000@18893.94\n"
                                                   "0.01256973@18891.92\n"
                                                   "----------------------\n"
                                                   "0.61103843@18888.14\n\n\n\n")
        self.message_helper("test_message_3.json", "0.37980402@18862.79\n"
                                                   "0.01504935@18862.79\n"
                                                   "0.02534887@18862.17\n"
                                                   "0.02534887@18862.03\n"
                                                   "0.00574054@18861.71\n"
                                                   "----------------------\n"
                                                   "0.06000000@18859.46\n"
                                                   "0.04500000@18859.46\n"
                                                   "0.00228234@18859.46\n"
                                                   "0.02196434@18859.08\n"
                                                   "0.05000000@18859.03\n\n\n\n")
        self.message_helper("test_message_4.json", "0.01197769@18866.10\n"
                                                   "0.00828186@18866.10\n"
                                                   "0.05000000@18866.10\n"
                                                   "0.00153006@18866.10\n"
                                                   "0.00254019@18866.10\n"
                                                   "----------------------\n"
                                                   "0.00400000@18865.38\n"
                                                   "0.02097098@18863.69\n"
                                                   "0.01504935@18863.55\n"
                                                   "0.10000000@18862.96\n"
                                                   "0.23726241@18857.63\n\n\n\n")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def message_helper(self, file_name, expected, mock_stdout):
        """
        helper function for testing websocket message_process function
        :param file_name: file name of the json message
        :param expected: expected output

        """
        order_book = OrderBook()
        client = CoinbaseWebsocketClient(order_book)
        f = open(file_name, "r")
        messages = json.load(f)
        for message in messages:
            client._process_message(None, message)
        client.order_book.print_price()
        self.assertEqual(mock_stdout.getvalue(), expected)


class TestOrderBook(unittest.TestCase):
    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_insert(self, mock_stdout):
        """
        Test insert orders
        """
        orderbook = OrderBook()
        orderbook.insert_order("1", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("2", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("3", size=Decimal("0.0001"), price=Decimal("200.1"), side="bid")
        orderbook.insert_order("4", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("5", size=Decimal("0.0001"), price=Decimal("201"), side="bid")
        orderbook.insert_order("6", size=Decimal("0.0001"), price=Decimal("201.1"), side="ask")
        orderbook.insert_order("7", size=Decimal("0.0001"), price=Decimal("201.1"), side="ask")
        orderbook.insert_order("8", size=Decimal("0.0001"), price=Decimal("201.2"), side="ask")
        orderbook.insert_order("9", size=Decimal("0.0001"), price=Decimal("201.11"), side="ask")
        orderbook.insert_order("10", size=Decimal("0.0001"), price=Decimal("201.11"), side="ask")
        orderbook.insert_order("11", size=Decimal("0.0001"), price=Decimal("201.12"), side="ask")

        self.assertEqual(orderbook._price_level["bid"], {Decimal("200.01"): ["1", "2", "4"],
                                                         Decimal("200.1"): ["3"], Decimal("201"): ["5"]})
        self.assertEqual(orderbook._price_level["ask"], {Decimal('201.1'): ['6', '7'],
                                                         Decimal('201.11'): ['9', '10'],
                                                         Decimal('201.12'): ['11'], Decimal('201.2'): ['8']})

        self.assertEqual(orderbook._orders["bid"], {"1": [Decimal("0.0001"), Decimal("200.01")],
                                                    "2": [Decimal("0.0001"), Decimal("200.01")],
                                                    "3": [Decimal("0.0001"), Decimal("200.1")],
                                                    "4": [Decimal("0.0001"), Decimal("200.01")],
                                                    "5": [Decimal("0.0001"), Decimal("201")]})

        self.assertEqual(orderbook._orders["ask"], {"6": [Decimal("0.0001"), Decimal("201.1")],
                                                    "7": [Decimal("0.0001"), Decimal("201.1")],
                                                    "8": [Decimal("0.0001"), Decimal("201.2")],
                                                    "9": [Decimal("0.0001"), Decimal("201.11")],
                                                    "10": [Decimal("0.0001"), Decimal("201.11")],
                                                    "11": [Decimal("0.0001"), Decimal("201.12")]})

        orderbook.print_price()
        self.assertEqual(mock_stdout.getvalue(), "0.0001@201.12\n0.0001@201.11\n0.0001@201.11\n0.0001@201.1\n"
                                                 "0.0001@201.1\n----------------------\n0.0001@201\n"
                                                 "0.0001@200.1\n0.0001@200.01\n0.0001@200.01\n0.0001@200.01\n\n\n\n")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_update(self, mock_stdout):
        """
        Test update order, either size or price or both
        """
        orderbook = OrderBook()
        orderbook.insert_order("1", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("2", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.change_order_size("3", size=Decimal("0.0002"), side="bid")
        orderbook.insert_order("3", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.change_order_size("3", size=Decimal("1"), side="bid")
        orderbook.insert_order("6", size=Decimal("0.0001"), price=Decimal("201.1"), side="ask")
        orderbook.change_order_price("6", old_price=Decimal("201.1"), new_price=Decimal("203.1"), side="ask")
        orderbook.change_order_size("6", size=Decimal("0.00005"), side="ask")

        self.assertEqual(orderbook._price_level["bid"], {Decimal("200.01"): ["1", "2", "3"]})
        self.assertEqual(orderbook._price_level["ask"], {Decimal("203.1"): ["6"]})
        self.assertEqual(orderbook._orders["bid"], {"1": [Decimal("0.0001"), Decimal("200.01")],
                                                    "2": [Decimal("0.0001"), Decimal("200.01")],
                                                    "3": [Decimal("1"), Decimal("200.01")]})

        self.assertEqual(orderbook._orders["ask"], {"6": [Decimal("0.00005"), Decimal("203.1")]})

        orderbook.print_price()
        self.assertEqual(mock_stdout.getvalue(), "0.00005@203.1\n----------------------\n"
                                                 "0.0001@200.01\n0.0001@200.01\n1@200.01\n\n\n\n")

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_delete(self, mock_stdout):
        """
        Test delete order
        """
        orderbook = OrderBook()
        orderbook.insert_order("1", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("2", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.delete_order("1", side="bid")
        orderbook.insert_order("3", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("6", size=Decimal("0.0001"), price=Decimal("201.1"), side="ask")
        orderbook.delete_order("6", side="ask")
        orderbook.insert_order("11", size=Decimal("0.001"), price=Decimal("202.1"), side="ask")

        self.assertEqual(orderbook._price_level["bid"], {Decimal("200.01"): ["2", "3"]})
        self.assertEqual(orderbook._price_level["ask"], {Decimal("202.1"): ["11"]})
        self.assertEqual(orderbook._orders["bid"], {"2": [Decimal("0.0001"), Decimal("200.01")],
                                                    "3": [Decimal("0.0001"), Decimal("200.01")]})

        self.assertEqual(orderbook._orders["ask"], {"11": [Decimal("0.001"), Decimal("202.1")]})

        orderbook.print_price()
        self.assertEqual(mock_stdout.getvalue(), "0.001@202.1\n----------------------\n"
                                                 "0.0001@200.01\n0.0001@200.01\n\n\n\n")

    def test_bid_crossover_ask(self):
        """
        Test bid price crossover ask price
        The orderbook should catch this error and raise an exception
        during the print_price() function for each tick
        """
        orderbook = OrderBook()
        orderbook.insert_order("1", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("2", size=Decimal("0.0001"), price=Decimal("200.01"), side="bid")
        orderbook.insert_order("11", size=Decimal("0.001"), price=Decimal("199.1"), side="ask")
        with self.assertRaises(Exception):
            orderbook.print_price()


if __name__ == '__main__':
    unittest.main()

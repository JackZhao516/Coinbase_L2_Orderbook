from collections import deque
from sortedcontainers import SortedDict
from decimal import Decimal


class OrderBook:
    """L2 order book"""

    def __init__(self):
        """
        initialize order book

        _price_level: dict of sorted dict, key is price, value is list of order id
        _orders: dict of orders dict, key is order id, value is list of [size, price]

        """
        self._orders = {"bid": {}, "ask": {}}
        self._price_level = {"bid": SortedDict(), "ask": SortedDict()}

    def _insert_price_level(self, price, side="bid"):
        """
        insert price level

        :param price: price level
        :param side: "bid" or "ask", default "bid"

        """
        if price not in self._price_level[side]:
            self._price_level[side][price] = []

    def insert_order(self, order_id, size, price, side="bid"):
        """
        insert order

        :param order_id: order id
        :param size: order size
        :param price: order price
        :param side: "bid" or "ask", default "bid"

        """
        self._insert_price_level(price, side)
        self._price_level[side][price].append(order_id)

        self._orders[side][order_id] = [size, price]

    def change_order_price(self, order_id, old_price, new_price, side="bid"):
        """
        change order price

        :param order_id: order id
        :param old_price: old order price
        :param new_price: new order price
        :param side: "bid" or "ask", default "bid"

        """
        if order_id in self._orders[side]:
            self._insert_price_level(new_price, side)
            self._price_level[side][new_price].append(order_id)
            self._orders[side][order_id][1] = new_price
            self._price_level[side][old_price].remove(order_id)
            if not self._price_level[side][old_price]:
                del self._price_level[side][old_price]

    def change_order_size(self, order_id, size, side="bid"):
        """
        change order size

        :param order_id: order id
        :param size: order size
        :param side: "bid" or "ask", default "bid"

        """
        if order_id in self._orders[side]:
            self._orders[side][order_id][0] = size

    def delete_order(self, order_id, side="bid"):
        """
        delete order

        :param order_id: order id
        :param side: "bid" or "ask", default "bid"

        """
        if order_id in self._orders[side]:
            price = self._orders[side][order_id][1]
            self._price_level[side][price].remove(order_id)
            if not self._price_level[side][price]:
                del self._price_level[side][price]
            del self._orders[side][order_id]

    def match_order(self, order_id, size, side="bid"):
        """
        match the completed order

        :param order_id: order id
        :param size: order complete size
        :param side: "bid" or "ask", default "bid"

        """
        if order_id in self._orders[side]:
            original_size = self._orders[side][order_id][0]
            if original_size == size:
                self.delete_order(order_id, side)
            elif original_size > size:
                self.change_order_size(order_id, original_size - size, side)

    def print_price(self):
        """
        print 5 best bid and ask price and size
        """
        ask, bid = 5, 5
        ask_stack = deque()
        for i in range(len(self._price_level["ask"])):
            _, ids = self._price_level["ask"].peekitem(i)
            num = min(ask, len(ids))
            for order_id in ids[:num]:
                ask_stack.appendleft(f"{self._orders['ask'][order_id][0]}@{self._orders['ask'][order_id][1]}")
            ask -= num
            if ask <= 0:
                break

        # make sure highest bid < lowest ask
        lowest_ask = ask_stack[-1].split("@")[1] if ask_stack else None
        highest_bid = self._price_level["bid"].peekitem(0)[0] if self._price_level["bid"] else None

        if lowest_ask and highest_bid:
            assert Decimal(lowest_ask) > Decimal(highest_bid), \
                f"lowest ask price {lowest_ask} is not greater than highest bid price {highest_bid}"

        # print out 5 best bid and ask price and size
        for i in range(len(ask_stack)):
            print(f"{ask_stack[0]}")
            ask_stack.popleft()

        print("----------------------")

        for i in range(len(self._price_level["bid"])):
            _, ids = self._price_level["bid"].peekitem(len(self._price_level["bid"]) - i - 1)
            num = min(bid, len(ids))
            for order_id in ids[:num]:
                print(f"{self._orders['bid'][order_id][0]}@{self._orders['bid'][order_id][1]}")
            bid -= num
            if bid <= 0:
                break

        print("\n\n")

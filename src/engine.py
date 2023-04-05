"""
This module contains the implementation of a simple matching engine that allows users to place
market and limit orders, as well as cancel and modify them.
"""
from order import Order
from book import Book
from typing import Dict


class MatchingEngine:
    """
    Implements a matching engine that supports order management for stocks. Supports extension
    for any number of stocks.

    Attributes:
        uid: Variable that stores the last assigned id to an order. It is incremented everytime an
            order is added.
        stock_set: A set of stocks that allows the extension of the matching engine to any number
            of stocks.
        books_map: A dictionary mapping stock names to their corresponding order books.
        orders_map: A dictionary mapping order unique IDs to their corresponding order objects.

    Notes:
        The orders_map and books_map are essential data structures to allow for fast search of
        orders by id, mainly for changing or deleting an order.
    """
    HELLO_MESSAGE = (
        "PyOME v0.1 - A Python Order Matching Engine\n"
        "Author: Henrique de Carvalho\n"
        "Type \"help\" to print commands."
    )
    PARSING_ERROR_MESSAGE = "Error: Parsing error."
    INACTIVE_ORDER_ERROR_MESSAGE = "Error: This order was executed or cancelled."
    INEXISTENT_ORDER_ERROR_MESSAGE = "Error: This order does not exist."
    EMPTY_ORDER_ERROR_MESSAGE = "Error: You cannot create or change an order to trade 0 shares."
    NO_LIQUIDITY_MESSAGE = "Order not executed due to no liquidity."
    ORDER_CREATED_MESSAGE = "Order created: {order}"
    ORDER_CHANGED_MESSAGE = "Order changed. New order: {new_order}"
    ORDER_CANCELLED_MESSAGE = "Order cancelled."
    TRADE_MESSAGE = "Trade, price: {price:.2f}, qty: {quantity}"
    HELP_MESSAGE = (
        "\n"
        "Commands:\n"
        "      limit <buy|sell:str> <price:float> <quantity:int>     places a limit order\n"
        "      market <buy|sell:str> <quantity:int>                  places a market order\n"
        "      cancel order <id:int>                                 cancels an order\n"
        "      change order <id:int> <price:float> <quantity:int>    changes an order\n"
        "      print book                                            prints the book of orders\n"
        "      help                                                  displays this message\n"
        "      exit                                                  exits engine\n"
    )
    EXIT_MESSAGE = "Exiting PyOME."

    def __init__(self):
        print(self.HELLO_MESSAGE)

        self.uid = 0
        self.stock_set = {"STOCK", }  # EXTEND: add stocks here or load from db
        self.books_map: Dict[str, Book] = {stock: Book(stock) for stock in self.stock_set}
        self.orders_map: Dict[int, Order] = {}

        self.loop = True
        self.repl()

    def repl(self) -> None:
        while self.loop:
            cmd = input(">>> ")
            return_msg = self.parse_and_execute(cmd)
            print(return_msg)

    def parse_and_execute(self, cmd: str) -> str:
        """
        Parse the input command string from the user and execute the corresponding action.

        Args:
            cmd: Input command string from the user containing the command to be parsed.

        Returns:
            Output message to be printed to the user.

        Notes:
            Orders with quantity = 0 are not allowed for security reasons. The Book class handles
            orders with quantity = 0, but adding such orders may cause the book to slow down or
            even experience a Denial of Service (DoS).
        """
        stock = "STOCK"  # EXTEND: remove default stock
        cmd_list = cmd.split()

        match cmd_list:
            # EXTEND: add [..., stock] to extend. If extended, stock requires parsing.
            case [ordtype, side, price, quantity] if ordtype == "limit":
                try:
                    quantity = self.parse_quantity(quantity)
                    price = self.parse_price(price)
                    side = self.parse_side(side)
                except ValueError:
                    return self.PARSING_ERROR_MESSAGE

                if quantity == 0:
                    return self.EMPTY_ORDER_ERROR_MESSAGE

                # Add new order to stock's book.
                order_id = self.new_uid()
                book = self.books_map[stock]
                order, trades = book.add_order(
                    order_id, Order.Type.LIMIT, side, quantity, price, stock
                )
                self.orders_map[order_id] = order

                if not trades:
                    return self.ORDER_CREATED_MESSAGE.format(order=order)

                output = []
                for quantity, price in trades:
                    output.append(self.TRADE_MESSAGE.format(price=price, quantity=quantity))
                if self.is_active_order(order_id):
                    output.append(self.ORDER_CREATED_MESSAGE.format(order=order))
                return "\n".join(output)

            # EXTEND: add [..., stock] to extend. If extended, stock requires parsing.
            case [ordtype, side, quantity] if ordtype == "market":
                try:
                    quantity = self.parse_quantity(quantity)
                    side = self.parse_side(side)
                except ValueError:
                    return self.PARSING_ERROR_MESSAGE

                if quantity == 0:
                    return self.EMPTY_ORDER_ERROR_MESSAGE

                # Add new order to stock's book.
                order_id = self.new_uid()
                book = self.books_map[stock]
                order, trades = book.add_order(
                    order_id, Order.Type.MARKET, side, quantity, stock=stock,
                )
                self.orders_map[order_id] = order

                # A market order has no reason to exist after executed.
                book.delete_order(order)

                if not trades:
                    return self.NO_LIQUIDITY_MESSAGE

                output = []
                for quantity, price in trades:
                    output.append(self.TRADE_MESSAGE.format(price=price, quantity=quantity))
                return "\n".join(output)

            case [op_a, op_b, order_id] if op_a == "cancel" and op_b == "order":
                try:
                    order_id = self.parse_order_id(order_id)
                except ValueError:
                    return self.PARSING_ERROR_MESSAGE

                try:
                    order = self.orders_map[order_id]
                except KeyError:
                    return self.INEXISTENT_ORDER_ERROR_MESSAGE

                if not self.is_active_order(order_id):
                    return self.INACTIVE_ORDER_ERROR_MESSAGE

                book = self.books_map[order.stock]
                book.delete_order(order)
                return self.ORDER_CANCELLED_MESSAGE

            case [op_a, op_b, order_id, price, quantity] if op_a == "change" and op_b == "order":
                try:
                    order_id = self.parse_order_id(order_id)
                    price = self.parse_price(price)
                    quantity = self.parse_quantity(quantity)
                except ValueError:
                    return self.PARSING_ERROR_MESSAGE

                if quantity == 0:
                    return self.EMPTY_ORDER_ERROR_MESSAGE

                try:
                    order = self.orders_map[order_id]
                except KeyError:
                    return self.INEXISTENT_ORDER_ERROR_MESSAGE

                if not self.is_active_order(order_id):
                    return self.INACTIVE_ORDER_ERROR_MESSAGE

                book = self.books_map[order.stock]
                new_order, trades = book.modify_order(
                     order=order,
                     quantity=quantity,
                     price=price,
                )
                self.orders_map[order_id] = new_order

                if not trades:
                    return self.ORDER_CHANGED_MESSAGE.format(new_order=new_order)

                output = []
                for quantity, price in trades:
                    output.append(self.TRADE_MESSAGE.format(price=price, quantity=quantity))
                if self.is_active_order(order_id):
                    output.append(self.ORDER_CHANGED_MESSAGE.format(new_order=new_order))
                return "\n".join(output)

            # EXTEND: add [..., stock] to generalize.
            case [op_a, op_b] if op_a == "print" and op_b == "book":
                book = self.books_map[stock]
                return book.__repr__()

            case [op_a] if op_a == "exit":
                self.loop = False
                return self.EXIT_MESSAGE

            case [op_a] if op_a == "help":
                return self.HELP_MESSAGE

            case _:
                return self.PARSING_ERROR_MESSAGE

    def new_uid(self):
        self.uid += 1
        return self.uid

    def is_valid_order(self, order_id: int) -> bool:
        return self.orders_map.get(order_id) is not None

    def is_active_order(self, order_id: int) -> bool:
        return self.orders_map[order_id].quantity != 0

    @staticmethod
    def parse_order_id(order_id: str) -> int:
        return int(order_id)

    @staticmethod
    def parse_price(price: str) -> float:
        return float(price)

    @staticmethod
    def parse_quantity(quantity: str) -> int:
        return int(quantity)

    @staticmethod
    def parse_side(side: str) -> Order.Side:
        if side == "buy":
            return Order.Side.BUY
        if side == "sell":
            return Order.Side.SELL
        raise ValueError


if __name__ == "__main__":
    MatchingEngine().repl()

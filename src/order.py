"""
This module contains the implementation of a class to represent a buy or sell order of a stock.
"""
from __future__ import annotations
import enum


class Order:
    """
    A class representing an individual order for a stock.

    Attributes:
        order_id: The unique identifier of the order.
        order_type: The type of the order (Order.Type.LIMIT | Order.Type.MARKET)
        order_side: The side of the order (Order.Type.BUY | Order.Type.SELL)
        quantity: The number of shares of the order.
        price: The price per share. Defaults to float("int").
        stock: The stock being traded. Defaults to "STOCK".

    Notes:
        `price` parameter defaults to float("int") because it is useful to the creation of
        market order, since this order has no price.
    """
    class Type(enum.Enum):
        MARKET = 1
        LIMIT = 2

    class Side(enum.Enum):
        BUY = 1
        SELL = 2

    def __init__(
            self, order_id: int, order_type: Type, order_side: Side,
            quantity: int, price: float, stock: str = "STOCK"
    ):
        self.order_id = order_id
        self.order_type = order_type
        self.order_side = order_side
        self.quantity = quantity
        self.price = price
        self.stock = stock

    def __lt__(self, other: Order) -> bool:
        """
        Compare two Order objects based on their price or, in case the prices are equal,
        based on their order_id.

        Essentially defines how orders should be prioritized in the Book. Lower sell orders have
        higher priority. Higher buy orders have higher priority. Orders that were placed earlier
        have higher priority than other orders with the same price.

        Args:
            other: Other Order object that is compared.

        Returns:
            True if the order that comes before the operator should be prioritized.

        Notes:
            This is done through __lt__() because the heapq is a min heap and uses '<' to compare
            objects. Therefore, if I want to heapify a list of objects, the best way to do it is
            through __lt__(). To achieve the effect of a max heap for buy orders, buy orders with
            greater price are read as being less than the other.
        """
        if self.order_side != other.order_side:
            raise Exception
        elif self.price == other.price:  # priority goes to lower id in case of tie
            return self.order_id < other.order_id
        elif self.order_side == Order.Side.SELL:
            return self.price < other.price
        elif self.order_side == Order.Side.BUY:
            return self.price > other.price
        else:
            raise Exception

    def __repr__(self) -> str:
        side: str = 'buy' if self.order_side == Order.Side.BUY else 'sell'
        return f"{side} {self.quantity} @ {self.price:.2f} ({self.order_id})"

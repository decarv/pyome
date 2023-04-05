"""
This module contains the implementation of a book class that manages an order book for a stock.
"""
import copy
import heapq
from order import Order
from typing import List, Tuple


class Book:
    """
    Implements a stock book that adds, modifies, deletes and matches orders.

    Attributes:
        stock: The stock being traded.
        sell_queue: The queue of sell orders, that is implemented as a min heap.
        buy_queue: The queue of buy orders, that is implemented as a max heap.

    Notes:
        The book is the main logic component of the Order Matching System. It is the actual
        responsible for matching the orders.
    """
    def __init__(self, stock: str):
        self.stock = stock
        self.sell_queue = []  # min heap
        self.buy_queue = []  # max heap

    def add_order(
            self, order_id: int, order_type: Order.Type, order_side: Order.Side,
            quantity: int, price: float = float("inf"), stock: str = "STOCK"
    ) -> Tuple[Order, List[Tuple[int, int]]]:
        """
        Creates and adds an order to the book and execute it as a limit order or a market order.

        Args:
            order_id: The unique identifier of the order.
            order_type: The type of the order (Order.Type.LIMIT | Order.Type.MARKET).
            order_side: The side of the order (Order.Type.BUY | Order.Type.SELL).
            quantity: The number of shares of the order.
            price: The price per share.
            stock: The stock being traded. Defaults to "STOCK".

        Returns:
            A tuple containing the Order object and a list of executed trades as tuples with
            quantity and price.
        """
        order = Order(order_id, order_type, order_side, quantity, price, stock)
        if order.order_type == Order.Type.LIMIT:
            return order, self.add_limit_order(order)
        else:  # order.order_side == Order.Type.MARKET
            return order, self.add_market_order(order)

    def add_limit_order(self, order: Order) -> List[Tuple[int, int]]:
        """
        Adds a limit order to the book and matches it against the best available existing orders,
        until the order is fulfilled (quantity = 0) or there are no more favorable orders available.

        Favorable orders have either equal price of the order or better (e.g. for a sell
        order, this means a buy order that offers equal or higher price). An order with the
        remaining quantity is placed if the quantity is not fulfilled. Has linearithmic
        worst-case time complexity, although this may not happen frequently.

        Args:
            order : The limit order to be added to the order book.

        Returns:
            A list of tuples representing any trades that were executed as a result of adding the
            new order. Each tuple contains two integers: the quantity and price of the executed
            trade.

        Notes:
            This function adds a limit order to the appropriate queue only after it matches it
            against any favorable orders in the opposite queue. Hence, the new order is added
            only if not completely executed. The compare() function is responsible for finding
            out if there are still favorable orders.
        """
        if order.order_side == Order.Side.BUY:
            queue = self.sell_queue
            order_queue = self.buy_queue
            def compare(x, y): return x >= y
        else:  # order_side == Order.Side.SELL
            queue = self.buy_queue
            order_queue = self.sell_queue
            def compare(x, y): return x <= y

        trades = []

        # Try to match opposite orders while it can.
        if queue:
            top_order = queue[0]
            while queue and order.quantity > 0 and compare(order.price, top_order.price):
                if order.quantity >= top_order.quantity:
                    # Ignore deleted orders.
                    if top_order.quantity > 0:
                        trades.append((top_order.quantity, top_order.price))
                        order.quantity -= top_order.quantity
                        top_order.quantity = 0
                    heapq.heappop(queue)
                    if queue:
                        top_order = queue[0]
                else:
                    top_order.quantity -= order.quantity
                    trades.append((order.quantity, top_order.price))
                    order.quantity = 0

        # Place order in queue if did not execute the whole quantity.
        if order.quantity > 0:
            heapq.heappush(order_queue, order)

        return trades

    def add_market_order(self, order: Order) -> List[Tuple[int, int]]:
        """
        Adds a market order to the book and matches it against the best available existing orders,
        until the order is fulfilled (quantity = 0) or there are no more orders available. Has
        linearithmic worst-case time complexity, although this may not happen frequently.

        Args:
            order : The limit order to be added to the order book.

        Returns:
            A list of tuples representing any trades that were executed as a result of adding the
            new order. Each tuple contains two integers: the quantity and price of the executed
            trade.
        """
        if order.order_side == Order.Side.BUY:
            queue = self.sell_queue
        else:  # order.order_side == Order.Type.SELL
            queue = self.buy_queue

        trades = []

        # Try to match opposite orders while it can.
        if queue:
            top_order = queue[0]
            while queue and order.quantity > 0:
                if order.quantity >= top_order.quantity:
                    # Ignore deleted orders.
                    if top_order.quantity > 0:
                        trades.append((top_order.quantity, top_order.price))
                        order.quantity -= top_order.quantity
                        top_order.quantity = 0
                    heapq.heappop(queue)
                    if queue:
                        top_order = queue[0]
                else:
                    top_order.quantity -= order.quantity
                    trades.append((order.quantity, top_order.price))
                    order.quantity = 0
        return trades

    # noinspection PyMethodMayBeStatic
    def delete_order(self, order: Order) -> None:
        """
        Deletes an order from the book in constant time.

        Args:
            order: the order to be deleted

        Notes:
            Setting the order's quantity to 0 is the way of removing orders. Previous iterations
            used heapq.heapify() and heapq.heappop() to achieve this, but it was unnecessary since
            the Book class already handles orders with quantity = 0 in the add_{limit|market}_order
            functions. It is important to note that the price of the order must be kept intact in
            order to maintain the heap invariant.
        """
        order.quantity = 0

    def modify_order(
            self, order: Order, quantity: int, price: float
    ) -> Tuple[Order, List[Tuple[int, int]]]:
        """
        Modifies an existing order by updating its quantity and/or price. Has worst-case
        logarithmic time complexity.

        Args:
            order: The order to be modified.
            quantity: The new quantity for the order.
            price: The new price for the order.

        Returns:
            A list of tuples representing any trades that were executed as a result of modifying the
            new order. Each tuple contains two integers: the quantity and price of the executed
            trade.

        Notes:
            To modify an order, the approach is to delete the existing order by setting its
            quantity to 0 and then adding a new order with the desired changes. In previous
            implementations, heapq.heapify() was used on the queue to adjust the order positions,
            but this operation had linear time complexity. Furthermore, since it's not feasible to
            consistently track the position of an order in the heap, using heapq._siftup() or
            heapq._siftdown() to adjust the heap in logarithmic time and eliminate the need for
            creating a new order isn't a viable option. Also, implementing a modified heap with
            maintained indices would introduce additional complexity, which is deemed excessive
            for the marginal benefits it would provide.
        """

        new_order_id, order.order_id = order.order_id, -1
        self.delete_order(order)
        return self.add_order(
            new_order_id,
            order.order_type,
            order.order_side,
            quantity,
            price,
            order.stock,
        )

    def __repr__(self) -> str:
        """
        Creates a table representation of the book, with buy and sell orders. Has best-case and
        worst-case linearithmic time complexity.

        Returns:
            Structured string representing a book, e.g.:

                   Buy Orders     |     Sell Orders
              -------------------------------------------
                 300 @ 10.01 (9)  |    200 @ 10.05 (10)
                 100 @ 9.99 (7)   |    100 @ 10.07 (11)
                 200 @ 9.98 (8)   |

        Notes:
            The columns are built based on at_idx, which is essentially the amount of written
            chars before @.

            For the buy column, since the amount of chars before @ needs to be (const_offset +
            col_width//2), if I want the @ in the middle of the column. (const_offset +
            col_width//2 - at_adx) is the number of spaces that need to be placed in l_offset.
            Experience has showed that it is not optimal to have the @ in the middle, so I added
            fine_offset. The same must be valid for the r_offset, where the numbers of chars
            after @ is (len(row) - at_idx - 1) the r_offset is (const_offset + col_width//2) - (
            len(row) - at_idx - 1).

            The same principles are valid for the sell orders column, except it does not have
            r_offset.
        """
        header = (
            "\n"
            "        Buy Orders     |     Sell Orders     \n"
            "  -------------------------------------------"
        )

        # Build body.
        col_width = 21
        const_offset = 2

        # Build buy orders column.
        buy_queue_copy = copy.deepcopy(self.buy_queue)
        buy_column = []
        while buy_queue_copy:
            el = heapq.heappop(buy_queue_copy)
            row = f"{el.quantity} @ {el.price:.2f} ({el.order_id})"
            if el.quantity <= 0:
                continue
            at_idx = row.find("@")
            fine_offset = 2
            l_offset = col_width//2 - at_idx + const_offset - fine_offset
            r_offset = col_width//2 - (len(row) - at_idx - 1) + fine_offset
            buy_column.append(" " * l_offset + row + " " * r_offset)

        # Build sell orders column.
        sell_queue_copy = copy.deepcopy(self.sell_queue)
        sell_column = []
        while sell_queue_copy:
            el = heapq.heappop(sell_queue_copy)
            if el.quantity <= 0:
                continue
            row = f"{el.quantity} @ {el.price:.2f} ({el.order_id})"
            at_idx = row.index("@")
            l_offset = col_width//2 - at_idx - const_offset
            sell_column.append(" " * l_offset + row)

        # Add blank rows where needed.
        while len(buy_column) > len(sell_column):
            sell_column.append(" " * col_width)
        while len(buy_column) < len(sell_column):
            buy_column.append(" " * (col_width + const_offset))

        # Build table.
        body = ""
        table_data = zip(buy_column, sell_column)
        for row in table_data:
            body += "\n"
            body += "|".join(row)
        body += "\n"
        return header + body

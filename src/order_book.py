from src.order import ActionType, Order, OrderStatus, OrderType


class OrderBook:
    """Manage buy and sell orders for one stock."""

    def __init__(self, stock: str):
        self.stock = stock
        self.bids = []
        self.asks = []
        self.last_trade_price = None

    def _sort_books(self):
        self.bids.sort(key=lambda order: order.price, reverse=True)
        self.asks.sort(key=lambda order: order.price)

    def get_quote(self):
        self._sort_books()
        best_bid = self.bids[0].price if self.bids else None
        best_ask = self.asks[0].price if self.asks else None
        return best_bid, best_ask, self.last_trade_price

    def _book_updater(self, new_order, counter_orders, price_check):
        remaining_quantity = new_order.get_quantity()
        index = 0

        while index < len(counter_orders) and remaining_quantity > 0:
            counter_order = counter_orders[index]
            if (
                new_order.action_type == ActionType.LIMIT
                and not price_check(new_order, counter_order)
            ):
                break

            fill_quantity = min(remaining_quantity, counter_order.get_quantity())
            if fill_quantity <= 0:
                index += 1
                continue

            # A resting limit order sets the execution price.
            trade_price = counter_order.price
            if new_order.execution_price is None:
                new_order.execution_price = trade_price
            if counter_order.execution_price is None:
                counter_order.execution_price = trade_price
            new_order.filling_update(fill_quantity)
            counter_order.filling_update(fill_quantity)
            self.last_trade_price = trade_price
            remaining_quantity = new_order.get_quantity()

            if counter_order.get_quantity() == 0:
                counter_orders.pop(index)
            else:
                index += 1

    def process_order(self, order):
        """Match an order and update the book."""
        if order.stock != self.stock:
            raise ValueError("Заявка относится к другой акции.")

        if order.action == OrderType.BUY:
            counter_orders = self.asks
            price_check = lambda new_order, match_order: new_order.price >= match_order.price
            resting_orders = self.bids
        else:
            counter_orders = self.bids
            price_check = lambda new_order, match_order: new_order.price <= match_order.price
            resting_orders = self.asks

        self._book_updater(order, counter_orders, price_check)

        if order.get_quantity() > 0:
            if order.action_type == ActionType.MARKET:
                order.status = OrderStatus.CANCELLED
            else:
                resting_orders.append(order)
                self._sort_books()

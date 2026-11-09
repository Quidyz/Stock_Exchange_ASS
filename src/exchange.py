from src.order import Order, OrderType
from src.order_book import OrderBook

class Exchange:
    """Главное управление всей биржей. Команды пользователя и хранит историю сделок/статусы заявок"""
    def __init__(self):
        self.books = {}
        self.orders_list = {}

    def _get_or_create_order(self, stock):
        if stock not in self.books:
            self.books[stock] = OrderBook(stock)
        return self.books[stock]

    def place_order(self, action: str, stock: str, action_type: str, price: float, quantity: int) -> Order:
        order = Order(
            stock=stock,
            action=action,
            action_type=action_type,
            price=price,
            quantity=quantity
        )

        book = self._get_or_create_order(stock)
        self.orders_list[order.id] = order
        try:
            book.process_order(order)
        except Exception:
            del self.orders_list[order.id]
            raise
        return order

    def get_sorted_orders_list(self):
        # Сортируем наш список акций по id
        sorted_order_list = sorted(self.orders_list.values(), key=lambda x: x.id)
        return sorted_order_list

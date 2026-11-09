import itertools
import math
from dataclasses import dataclass, field
from enum import Enum


class ActionType(Enum):
    LIMIT = 'LMT'
    MARKET = 'MKT'

class OrderType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class OrderStatus(Enum):
    PENDING = 'PENDING'
    PARTIAL = 'PARTIAL'
    FILLED = 'FILLED'
    CANCELLED = 'CANCELLED'

# простой вариант счетчика
_id_counter = itertools.count(1)

@dataclass
class Order:
    """Класс Заявок, хранит детали"""
    id: int = field(init=False) # --> __post_init__
    stock: str # stock name
    action: OrderType # BUY | SELL
    action_type: ActionType # LMT | MKT
    quantity: int # Count of action
    price: float | None = None # Price of action

    execution_price: float | None = None # for MKT trade
    filled_quantity: int = 0 # Quantity counter for status
    status: OrderStatus = OrderStatus.PENDING

    def __post_init__(self):
        # А теперь подумай - зачем же ты сюда это пихнул? Да, он создается к каждой отдельно
        self.id: int = next(_id_counter)
        self._validation()

    def _validation(self):
        """Проверка типа продажи и количества"""
        if self.quantity <= 0:
            raise ValueError("Количество должно быть положительным.")

        if self.action_type == ActionType.LIMIT:
            if self.price is None or not math.isfinite(self.price) or self.price <= 0:
                raise ValueError("Цена лимитной заявки должна быть конечной и положительной.")

        if self.action_type == ActionType.MARKET and self.price is not None:
            raise ValueError("Для рыночной заявки цена не нужна.")

    def get_quantity(self) -> int:
        return self.quantity - self.filled_quantity

    def filling_update(self, new_quantity):
        """Обновление статуса заявки"""
        if new_quantity <= 0:
            raise ValueError("Количество акций должно быть положительным.")

        new_filled_quantity = self.filled_quantity + new_quantity
        if new_filled_quantity > self.quantity:
            raise ValueError("Количество покупаемых акций не должно превышать количество в заявке.")

        self.filled_quantity = new_filled_quantity

        if self.filled_quantity == self.quantity:
            self.status = OrderStatus.FILLED
        elif self.filled_quantity < self.quantity:
            self.status = OrderStatus.PARTIAL
        else:
            self.status = OrderStatus.PENDING
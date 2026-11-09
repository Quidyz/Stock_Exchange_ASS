import pytest

from src.order import ActionType, Order, OrderType


@pytest.mark.parametrize("price", [float("nan"), float("inf"), float("-inf")])
def test_limit_order_rejects_non_finite_price(price):
    with pytest.raises(ValueError, match="конечной"):
        Order(
            stock="XYZ",
            action=OrderType.BUY,
            action_type=ActionType.LIMIT,
            quantity=1,
            price=price,
        )

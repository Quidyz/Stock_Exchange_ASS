import pytest

from src.order import ActionType, Order, OrderStatus, OrderType
from src.order_book import OrderBook


def make_order(side, kind, quantity, price=None):
    return Order(
        stock="XYZ",
        action=side,
        action_type=kind,
        quantity=quantity,
        price=price,
    )


def test_market_buy_executes_at_best_ask():
    book = OrderBook("XYZ")
    ask = make_order(OrderType.SELL, ActionType.LIMIT, 3, 10)
    book.process_order(ask)

    market_buy = make_order(OrderType.BUY, ActionType.MARKET, 2)
    book.process_order(market_buy)

    assert market_buy.status == OrderStatus.FILLED
    assert market_buy.execution_price == 10
    assert ask.get_quantity() == 1
    assert not book.bids


def test_market_sell_executes_at_best_bid():
    book = OrderBook("XYZ")
    bid = make_order(OrderType.BUY, ActionType.LIMIT, 3, 11)
    book.process_order(bid)

    market_sell = make_order(OrderType.SELL, ActionType.MARKET, 2)
    book.process_order(market_sell)

    assert market_sell.status == OrderStatus.FILLED
    assert market_sell.execution_price == 11
    assert bid.get_quantity() == 1
    assert not book.asks


@pytest.mark.parametrize("side", [OrderType.BUY, OrderType.SELL])
def test_unfilled_market_order_is_cancelled_not_added_to_book(side):
    book = OrderBook("XYZ")
    market_order = make_order(side, ActionType.MARKET, 2)

    book.process_order(market_order)

    assert market_order.status == OrderStatus.CANCELLED
    assert market_order.get_quantity() == 2
    assert not book.bids
    assert not book.asks


def test_market_order_cancels_unfilled_remainder_after_partial_execution():
    book = OrderBook("XYZ")
    ask = make_order(OrderType.SELL, ActionType.LIMIT, 1, 10)
    book.process_order(ask)
    market_buy = make_order(OrderType.BUY, ActionType.MARKET, 3)

    book.process_order(market_buy)

    assert market_buy.status == OrderStatus.CANCELLED
    assert market_buy.filled_quantity == 1
    assert market_buy.get_quantity() == 2
    assert not book.bids
    assert not book.asks


def test_limit_order_matches_multiple_counter_orders_without_skipping():
    book = OrderBook("XYZ")
    first_ask = make_order(OrderType.SELL, ActionType.LIMIT, 1, 10)
    second_ask = make_order(OrderType.SELL, ActionType.LIMIT, 1, 11)
    book.process_order(first_ask)
    book.process_order(second_ask)

    buy = make_order(OrderType.BUY, ActionType.LIMIT, 2, 12)
    book.process_order(buy)

    assert buy.status == OrderStatus.FILLED
    assert buy.filled_quantity == 2
    assert buy.execution_price == 10
    assert not book.asks
    assert book.last_trade_price == 11

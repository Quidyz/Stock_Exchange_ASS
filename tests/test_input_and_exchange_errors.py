from src.exchange import Exchange
from src.order import ActionType, OrderType
from src.parser import Parser


def test_market_order_with_no_liquidity_reports_cancellation(capsys):
    parser = Parser(Exchange())

    parser.trade_command("BUY", ["XYZ", "MKT", "2"])

    output = capsys.readouterr().out
    assert "Рыночная заявка отменена" in output
    assert "не исполнено 2 из 2" in output


def test_unfilled_market_order_is_listed_as_cancelled_without_price(capsys):
    exchange = Exchange()
    parser = Parser(exchange)
    market_order = exchange.place_order(
        action=OrderType.BUY,
        stock="XYZ",
        action_type=ActionType.MARKET,
        price=None,
        quantity=2,
    )

    parser.view_command("VIEW", ["ORDERS"])

    output = capsys.readouterr().out
    assert market_order.status.name == "CANCELLED"
    assert "CANCELLED" in output
    assert "—" in output
    assert "$None" not in output


def test_view_orders_shows_zero_execution_price(capsys):
    exchange = Exchange()
    parser = Parser(exchange)
    order = exchange.place_order(
        action=OrderType.BUY,
        stock="XYZ",
        action_type=ActionType.LIMIT,
        price=1,
        quantity=1,
    )
    order.execution_price = 0

    parser.view_command("VIEW", ["ORDERS"])

    assert "$0" in capsys.readouterr().out

from unittest.mock import Mock

import pytest

from src.exchange import Exchange
from src.parser import Parser


def test_empty_quote_command_prints_usage_instead_of_raising(capsys):
    parser = Parser(Exchange())

    parser.quote_command("QUOTE", [])

    assert "Формат команды: QUOTE <тикер>" in capsys.readouterr().out


def test_quote_command_rejects_extra_arguments(capsys):
    parser = Parser(Exchange())

    parser.quote_command("QUOTE", ["XYZ", "EXTRA"])

    assert "Формат команды: QUOTE <тикер>" in capsys.readouterr().out


def test_empty_trade_command_prints_error_instead_of_raising(capsys):
    parser = Parser(Exchange())

    parser.trade_command("BUY", [])

    assert "Ошибка" in capsys.readouterr().out


def test_failed_order_processing_does_not_leave_order_in_history():
    exchange = Exchange()
    book = exchange._get_or_create_order("XYZ")
    book.process_order = Mock(side_effect=RuntimeError("matching failed"))

    with pytest.raises(RuntimeError, match="matching failed"):
        exchange.place_order("BUY", "XYZ", "LMT", 10, 1)

    assert exchange.orders_list == {}

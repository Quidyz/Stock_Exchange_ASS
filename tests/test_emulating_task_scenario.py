import pytest, builtins
from src.exchange import Exchange
from src.parser import Parser


def test_full_scenario(capsys):
    """Checking the example from the task"""
    core = Exchange()
    parser = Parser(core=core)

    # 1. BUY SNAP LMT $30 100
    parser.trade_command("BUY", ["SNAP", "LMT", "$30", "100"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1] == ("Вы разместили лимитную заявку на покупку 100 акций SNAP по цене $30.0 за штуку.")

    # 2. BUY FB MKT 20
    parser.trade_command("BUY", ["FB", "MKT", "20"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1] == "Рыночная заявка отменена: не исполнено 20 из 20 акций FB."

    # 3. SELL FB LMT $20.00 20
    parser.trade_command("SELL", ["FB", "LMT", "$20.00", "20"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1] == ("Вы разместили лимитную заявку на продажу 20 акций FB по цене $20.0 за штуку.")

    # 4. SELL SNAP LMT $30.00 20
    parser.trade_command("SELL", ["SNAP", "LMT", "$30.00", "20"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1] == ("Вы разместили лимитную заявку на продажу 20 акций SNAP по цене $30.0 за штуку.")

    # 5. SELL SNAP LMT $31.00 10
    parser.trade_command("SELL", ["SNAP", "LMT", "$31.00", "10"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1] == ("Вы разместили лимитную заявку на продажу 10 акций SNAP по цене $31.0 за штуку.")

    # 8. VIEW ORDERS
    parser.view_command("VIEW", ["ORDERS"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-5] == "1. SNAP LMT BUY $30.0 100 20/100 PARTIAL"
    assert out[-4] == "2. FB MKT BUY — 20 0/20 CANCELLED"
    assert out[-3] == "3. FB LMT SELL $20.0 20 0/20 PENDING"
    assert out[-2] == "4. SNAP LMT SELL $30.0 20 20/20 FILLED"
    assert out[-1] == "5. SNAP LMT SELL $31.0 10 0/10 PENDING"

    # 10. QUOTE SNAP
    parser.quote_command("QUOTE", ["SNAP"])
    out = capsys.readouterr().out.strip().splitlines()
    assert out[-1] == "SNAP BID: $30.0 ASK: $31.0 LAST: $30.0"
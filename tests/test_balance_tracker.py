from portfolio.balance_tracker import BalanceTracker


def test_balance_tracker_default_initial_cash_is_20_usdt():
    t = BalanceTracker()
    assert t.cash == 20.0


def test_balance_tracker_can_override_initial_cash():
    t = BalanceTracker(cash=50.0)
    assert t.cash == 50.0

from strategies.arbitrage_strategy import ArbitrageStrategy


def test_arbitrage_strategy_generates_signal():
    s = ArbitrageStrategy(min_edge_bps=100)
    s.on_market_update([{"id": "m1", "yes_price": 0.45, "no_price": 0.53}])
    signals = s.generate_signals()
    assert len(signals) == 1
    assert signals[0]["market"] == "m1"

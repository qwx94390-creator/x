from core.engine import TradingEngine
from strategies.arbitrage_strategy import ArbitrageStrategy
from strategies.hybrid_strategy import HybridStrategy
from strategies.trend_following import TrendFollowingStrategy


def test_strategy_runtime_fields_for_arbitrage() -> None:
    fields = TradingEngine._strategy_runtime_fields(ArbitrageStrategy(min_edge_bps=90))
    assert fields["min_edge_bps"] == 90
    assert fields["strategy_mode"] == "ArbitrageStrategy"


def test_strategy_runtime_fields_for_trend() -> None:
    fields = TradingEngine._strategy_runtime_fields(TrendFollowingStrategy(threshold_bps=55))
    assert fields["trend_threshold_bps"] == 55
    assert "min_edge_bps" not in fields


def test_strategy_runtime_fields_for_hybrid_no_crash() -> None:
    s = HybridStrategy([ArbitrageStrategy(min_edge_bps=80), TrendFollowingStrategy(threshold_bps=60)])
    fields = TradingEngine._strategy_runtime_fields(s)
    assert fields["strategy_mode"] == "HybridStrategy"

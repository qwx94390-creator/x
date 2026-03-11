from core.service_container import _build_strategy
from strategies.arbitrage_strategy import ArbitrageStrategy
from strategies.hybrid_strategy import HybridStrategy
from strategies.trend_following import TrendFollowingStrategy


def test_build_strategy_hybrid_default() -> None:
    s = _build_strategy({"risk": {"min_edge_bps": 80}})
    assert isinstance(s, HybridStrategy)


def test_build_strategy_arbitrage_mode() -> None:
    s = _build_strategy({"strategy": {"mode": "arbitrage"}, "risk": {"min_edge_bps": 80}})
    assert isinstance(s, ArbitrageStrategy)


def test_build_strategy_trend_mode() -> None:
    s = _build_strategy({"strategy": {"mode": "trend"}, "risk": {"min_edge_bps": 80}})
    assert isinstance(s, TrendFollowingStrategy)

from analytics.daily_report import DailyReporter
from analytics.metrics import MetricsCollector
from diagnostics.llm_advisor import LLMAdvisor
from strategies.arbitrage_strategy import ArbitrageStrategy


def test_metrics_roll_day_returns_previous_snapshot_and_resets() -> None:
    m = MetricsCollector()
    m.record_signal({"yes_price": 0.4, "no_price": 0.5})
    m.record_fill({"size": 10, "price": 0.4})
    m.record_realized_pnl(1.2)

    prev = m.roll_day_if_needed("2099-01-01")
    assert prev is not None
    assert prev["signals"] == 1
    assert prev["fills"] == 1
    assert prev["daily_realized_pnl"] == 1.2

    now = m.snapshot()
    assert now["signals"] == 0
    assert now["fills"] == 0


def test_daily_report_reason_and_strategy_tune() -> None:
    reporter = DailyReporter()
    report = reporter.build_report(
        day="2026-01-01",
        snapshot={
            "daily_realized_pnl": -1.5,
            "volume": 100.0,
            "fills": 3,
            "signals": 5,
            "rejected": 2,
            "avg_edge_bps": 50.0,
        },
    )
    assert "风控拒单" in report.reason
    assert "套利空间不足" in report.reason

    s = ArbitrageStrategy(min_edge_bps=80)
    s.tune_from_pnl(report.pnl)
    assert s.min_edge_bps == 90


def test_llm_advisor_fallback_when_not_configured() -> None:
    advisor = LLMAdvisor(base_url="", api_key="", model="")
    msg = advisor.diagnose({"pnl": 1.0})
    assert "disabled" in msg


def test_metrics_record_fill_uses_fallback_price_when_fill_price_is_zero() -> None:
    m = MetricsCollector()
    m.record_fill({"size": 25, "price": 0.0}, fallback_price=0.42)
    snap = m.snapshot()
    assert snap["fills"] == 1
    assert snap["volume"] == 10.5
    assert snap["zero_price_fills"] == 1

from dataclasses import dataclass

from analytics.daily_report import DailyReporter
from analytics.metrics import MetricsCollector
from data.market_data_service import MarketDataService
from database.postgres import Database
from diagnostics.llm_advisor import LLMAdvisor
from execution.execution_engine import ExecutionEngine
from execution.order_router import PaperOrderRouter
from notifications.feishu import FeishuNotifier
from notifications.multi import MultiNotifier
from notifications.telegram import TelegramNotifier
from portfolio.balance_tracker import BalanceTracker
from portfolio.position_manager import PositionManager
from risk.risk_engine import RiskEngine
from strategies.arbitrage_strategy import ArbitrageStrategy
from strategies.base_strategy import BaseStrategy
from strategies.hybrid_strategy import HybridStrategy
from strategies.trend_following import TrendFollowingStrategy


@dataclass
class Services:
    market_data: MarketDataService
    strategy: BaseStrategy
    risk: RiskEngine
    router: PaperOrderRouter
    execution: ExecutionEngine
    positions: PositionManager
    balance: BalanceTracker
    database: Database
    metrics: MetricsCollector
    reporter: DailyReporter
    advisor: LLMAdvisor
    notifier: MultiNotifier


def _build_strategy(config: dict) -> BaseStrategy:
    strategy_cfg = config.get("strategy", {})
    mode = strategy_cfg.get("mode", "hybrid")

    arbitrage = ArbitrageStrategy(min_edge_bps=config.get("risk", {}).get("min_edge_bps", 80))
    trend = TrendFollowingStrategy(
        lookback=strategy_cfg.get("trend_lookback", 5),
        threshold_bps=strategy_cfg.get("trend_threshold_bps", 50),
        size=strategy_cfg.get("trend_size", 15.0),
    )

    if mode == "arbitrage":
        return arbitrage
    if mode == "trend":
        return trend
    return HybridStrategy([arbitrage, trend])


def build_services(config: dict) -> Services:
    polymarket_cfg = config.get("polymarket", {})
    risk_cfg = config.get("risk", {})
    notifications_cfg = config.get("notifications", {})
    portfolio_cfg = config.get("portfolio", {})
    llm_cfg = config.get("llm", {})

    market_data = MarketDataService(polymarket_cfg["api_url"])
    strategy = _build_strategy(config)
    risk = RiskEngine(
        max_order_size=risk_cfg["max_order_size"],
        max_position_notional=risk_cfg["max_position_notional"],
    )
    router = PaperOrderRouter()
    execution = ExecutionEngine(router)
    positions = PositionManager()
    balance = BalanceTracker(cash=portfolio_cfg.get("initial_cash_usdt", 20.0))
    database = Database(config["database"]["url"])
    metrics = MetricsCollector()
    reporter = DailyReporter()
    advisor = LLMAdvisor(
        provider=llm_cfg.get("provider", "openai_compatible"),
        api_key=llm_cfg.get("api_key", ""),
        model=llm_cfg.get("model", ""),
        base_url=llm_cfg.get("base_url", ""),
    )
    telegram = TelegramNotifier(
        token=notifications_cfg.get("telegram_token", ""),
        chat_id=notifications_cfg.get("telegram_chat_id", ""),
    )
    feishu = FeishuNotifier(webhook_url=notifications_cfg.get("feishu_webhook_url", ""))
    notifier = MultiNotifier([telegram, feishu])
    return Services(market_data, strategy, risk, router, execution, positions, balance, database, metrics, reporter, advisor, notifier)
    telegram = TelegramNotifier(
        token=config["notifications"].get("telegram_token", ""),
        chat_id=config["notifications"].get("telegram_chat_id", ""),
    )
    feishu = FeishuNotifier(webhook_url=config["notifications"].get("feishu_webhook_url", ""))
    notifier = MultiNotifier([telegram, feishu])
    return Services(market_data, strategy, risk, router, execution, positions, database, metrics, notifier)

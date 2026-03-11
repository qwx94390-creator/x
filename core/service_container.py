from dataclasses import dataclass

from analytics.metrics import MetricsCollector
from data.market_data_service import MarketDataService
from database.postgres import Database
from execution.execution_engine import ExecutionEngine
from execution.order_router import PaperOrderRouter
from notifications.feishu import FeishuNotifier
from notifications.multi import MultiNotifier
from notifications.telegram import TelegramNotifier
from portfolio.balance_tracker import BalanceTracker
from portfolio.position_manager import PositionManager
from risk.risk_engine import RiskEngine
from strategies.arbitrage_strategy import ArbitrageStrategy


@dataclass
class Services:
    market_data: MarketDataService
    strategy: ArbitrageStrategy
    risk: RiskEngine
    router: PaperOrderRouter
    execution: ExecutionEngine
    positions: PositionManager
    balance: BalanceTracker
    database: Database
    metrics: MetricsCollector
    notifier: MultiNotifier


def build_services(config: dict) -> Services:
    market_data = MarketDataService(config["polymarket"]["api_url"])
    strategy = ArbitrageStrategy(min_edge_bps=config["risk"]["min_edge_bps"])
    risk = RiskEngine(
        max_order_size=config["risk"]["max_order_size"],
        max_position_notional=config["risk"]["max_position_notional"],
    )
    router = PaperOrderRouter()
    execution = ExecutionEngine(router)
    positions = PositionManager()
    balance = BalanceTracker(cash=config.get("portfolio", {}).get("initial_cash_usdt", 20.0))
    database = Database(config["database"]["url"])
    metrics = MetricsCollector()
    telegram = TelegramNotifier(
        token=config["notifications"].get("telegram_token", ""),
        chat_id=config["notifications"].get("telegram_chat_id", ""),
    )
    feishu = FeishuNotifier(webhook_url=config["notifications"].get("feishu_webhook_url", ""))
    notifier = MultiNotifier([telegram, feishu])
    return Services(market_data, strategy, risk, router, execution, positions, balance, database, metrics, notifier)

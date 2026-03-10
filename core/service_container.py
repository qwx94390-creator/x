from dataclasses import dataclass

from analytics.metrics import MetricsCollector
from data.market_data_service import MarketDataService
from database.postgres import Database
from execution.execution_engine import ExecutionEngine
from execution.order_router import PaperOrderRouter
from notifications.telegram import TelegramNotifier
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
    database: Database
    metrics: MetricsCollector
    notifier: TelegramNotifier


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
    database = Database(config["database"]["url"])
    metrics = MetricsCollector()
    notifier = TelegramNotifier(
        token=config["notifications"]["telegram_token"],
        chat_id=config["notifications"]["telegram_chat_id"],
    )
    return Services(market_data, strategy, risk, router, execution, positions, database, metrics, notifier)

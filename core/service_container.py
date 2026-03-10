from dataclasses import dataclass
from typing import Protocol

from analytics.metrics import MetricsCollector
from data.market_data_service import MarketDataService
from database.postgres import Database
from execution.clob_client import ClobClient
from execution.execution_engine import ExecutionEngine
from execution.order_router import PaperOrderRouter, PolymarketOrderRouter
from execution.wallet_signer import WalletSigner
from notifications.telegram import TelegramNotifier
from portfolio.position_manager import PositionManager
from risk.risk_engine import RiskEngine
from strategies.arbitrage_strategy import ArbitrageStrategy


class OrderRouterLike(Protocol):
    async def send(self, order: dict) -> dict:
        ...


@dataclass
class Services:
    market_data: MarketDataService
    strategy: ArbitrageStrategy
    risk: RiskEngine
    router: OrderRouterLike
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

    mode = config.get("app", {}).get("mode", "paper")
    if mode == "live":
        signer = WalletSigner(
            api_key=config.get("polymarket", {}).get("api_key", ""),
            api_secret=config.get("polymarket", {}).get("api_secret", ""),
            passphrase=config.get("polymarket", {}).get("passphrase", ""),
        )
        client = ClobClient(config["polymarket"]["api_url"])
        router: OrderRouterLike = PolymarketOrderRouter(client=client, signer=signer)
    else:
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

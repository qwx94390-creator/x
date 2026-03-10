import asyncio
from datetime import datetime, timezone

from core.logger import setup_logger
from core.service_container import Services


class TradingEngine:
    def __init__(self, services: Services) -> None:
        self.s = services
        self.logger = setup_logger(level="INFO")

    async def setup(self) -> None:
        await self.s.database.connect()
        await self.s.database.create_tables()

    async def run_once(self) -> None:
        markets = await self.s.market_data.get_markets(limit=20)
        self.s.strategy.on_market_update(markets)
        signals = self.s.strategy.generate_signals()

        for signal in signals:
            if not self.s.risk.check_signal(signal, self.s.positions):
                self.logger.warning("signal rejected by risk: %s", signal)
                continue
            order = self.s.execution.build_order(signal)
            result = await self.s.execution.execute(order)
            if result["status"] == "filled":
                self.s.positions.apply_fill(result)
                await self.s.database.insert_trade({
                    "market": result["market"],
                    "side": result["side"],
                    "price": result["price"],
                    "size": result["size"],
                    "ts": datetime.now(timezone.utc),
                })
                self.s.metrics.record_fill(result)

        summary = self.s.metrics.snapshot()
        self.logger.info("cycle summary: %s", summary)
        self.s.notifier.send_message(f"cycle done: {summary}")

    async def run_forever(self, interval_sec: int = 5) -> None:
        await self.setup()
        while True:
            await self.run_once()
            await asyncio.sleep(interval_sec)

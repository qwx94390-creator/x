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

    @staticmethod
    def _strategy_runtime_fields(strategy: object) -> dict:
        fields = {
            "strategy_mode": strategy.__class__.__name__,
            "min_edge_bps": getattr(strategy, "min_edge_bps", None),
            "trend_threshold_bps": getattr(strategy, "threshold_bps", None),
        }
        return {k: v for k, v in fields.items() if v is not None}

    def _estimate_trade_pnl(self, signal: dict, result: dict) -> float:
        edge = 1.0 - float(signal.get("yes_price", 0.0)) - float(signal.get("no_price", 0.0))
        size = float(result.get("size", 0.0))
        return max(-size, edge * size)

    def _maybe_send_daily_report(self) -> None:
        day = datetime.now(timezone.utc).date().isoformat()
        snapshot = self.s.metrics.roll_day_if_needed(day)
        if snapshot is None:
            return

        report = self.s.reporter.build_report(day=snapshot["day"], snapshot=snapshot)
        llm_payload = {
            "day": report.day,
            "pnl": report.pnl,
            "volume": report.volume,
            "fills": report.fills,
            "signals": report.signals,
            "rejected": report.rejected,
            "avg_edge_bps": report.avg_edge_bps,
            "reason": report.reason,
            "cash": self.s.balance.cash,
        }
        llm_payload.update(self._strategy_runtime_fields(self.s.strategy))

        llm_advice = self.s.advisor.diagnose(llm_payload)
        msg = self.s.reporter.render_message(report, llm_advice)
        self.s.notifier.send_message(msg)
        self.s.strategy.tune_from_pnl(report.pnl)
        self.logger.info("daily report sent. strategy fields=%s", self._strategy_runtime_fields(self.s.strategy))

    async def run_once(self) -> None:
        markets = await self.s.market_data.get_markets(limit=20)
        self.s.strategy.on_market_update(markets)
        signals = self.s.strategy.generate_signals()

        for signal in signals:
            if not self.s.risk.check_signal(signal, self.s.positions):
            self.s.metrics.record_signal(signal)
            if not self.s.risk.check_signal(signal, self.s.positions):
                self.s.metrics.record_rejection()
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
                pnl = self._estimate_trade_pnl(signal, result)
                self.s.balance.apply_pnl(pnl)
                self.s.metrics.record_realized_pnl(pnl)
                self.s.metrics.record_fill(result, fallback_price=float(signal.get("yes_price", 0.0)))

        summary = self.s.metrics.snapshot()
        summary["cash"] = round(self.s.balance.cash, 4)
        summary.update(self._strategy_runtime_fields(self.s.strategy))
        if summary.get("fills", 0) > 0 and summary.get("volume", 0.0) == 0.0:
            self.logger.warning("anomaly detected: fills=%s but volume=0.0; check feed price fields", summary.get("fills"))
        self.logger.info("cycle summary: %s", summary)
        self.s.notifier.send_message(f"cycle done: {summary}")
        self._maybe_send_daily_report()

    async def run_forever(self, interval_sec: int = 5) -> None:
        await self.setup()
        while True:
            await self.run_once()
            await asyncio.sleep(interval_sec)

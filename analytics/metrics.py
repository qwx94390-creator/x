from datetime import date
from typing import Optional


class MetricsCollector:
    def __init__(self) -> None:
        self._day = date.today().isoformat()
        self._reset_counters()

    def _reset_counters(self) -> None:
        self.fills = 0
        self.volume = 0.0
        self.signals = 0
        self.rejected = 0
        self.total_edge_bps = 0.0
        self._daily_realized_pnl = 0.0

    def record_signal(self, signal: dict) -> None:
        self.signals += 1
        yes_price = float(signal.get("yes_price", 0.0))
        no_price = float(signal.get("no_price", 0.0))
        edge_bps = max(0.0, (1.0 - (yes_price + no_price)) * 10000)
        self.total_edge_bps += edge_bps

    def record_rejection(self) -> None:
        self.rejected += 1

    def record_fill(self, fill: dict) -> None:
        self.fills += 1
        self.volume += fill["size"] * fill["price"]

    def record_realized_pnl(self, pnl: float) -> None:
        self._daily_realized_pnl += pnl

    def snapshot(self) -> dict:
        avg_edge_bps = self.total_edge_bps / self.signals if self.signals else 0.0
        return {
            "day": self._day,
            "fills": self.fills,
            "volume": round(self.volume, 4),
            "signals": self.signals,
            "rejected": self.rejected,
            "avg_edge_bps": round(avg_edge_bps, 2),
            "daily_realized_pnl": round(self._daily_realized_pnl, 4),
        }

    def roll_day_if_needed(self, current_day: str) -> Optional[dict]:
        if current_day == self._day:
            return None
        prev = self.snapshot()
        self._day = current_day
        self._reset_counters()
        return prev

from collections import defaultdict, deque

from strategies.base_strategy import BaseStrategy


class TrendFollowingStrategy(BaseStrategy):
    def __init__(self, lookback: int = 5, threshold_bps: int = 50, size: float = 15.0) -> None:
        super().__init__()
        self.lookback = max(2, lookback)
        self.threshold_bps = threshold_bps
        self.size = size
        self._hist: dict[str, deque[float]] = defaultdict(lambda: deque(maxlen=self.lookback))

    def on_market_update(self, market_data: list[dict]) -> None:
        super().on_market_update(market_data)
        for m in market_data:
            mid = str(m["id"])
            self._hist[mid].append(float(m.get("yes_price", 0.0)))

    def tune_from_pnl(self, daily_pnl: float) -> None:
        if daily_pnl < 0:
            self.threshold_bps = min(300, self.threshold_bps + 10)
        elif daily_pnl > 0:
            self.threshold_bps = max(20, self.threshold_bps - 5)

    def generate_signals(self) -> list[dict]:
        signals: list[dict] = []
        for m in self.market_data:
            mid = str(m["id"])
            prices = self._hist[mid]
            if len(prices) < self.lookback:
                continue
            move_bps = (prices[-1] - prices[0]) * 10000
            if move_bps >= self.threshold_bps:
                signals.append(
                    {
                        "type": "trend_following",
                        "market": mid,
                        "yes_price": float(m["yes_price"]),
                        "no_price": float(m["no_price"]),
                        "size": self.size,
                    }
                )
        return signals

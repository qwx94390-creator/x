from strategies.base_strategy import BaseStrategy


class ArbitrageStrategy(BaseStrategy):
    def __init__(self, min_edge_bps: int = 80) -> None:
        super().__init__()
        self.min_edge_bps = min_edge_bps

    def tune_from_pnl(self, daily_pnl: float) -> None:
        if daily_pnl < 0:
            self.min_edge_bps = min(300, self.min_edge_bps + 10)
        elif daily_pnl > 0:
            self.min_edge_bps = max(40, self.min_edge_bps - 5)

    def generate_signals(self) -> list[dict]:
        signals: list[dict] = []
        threshold = 1.0 - self.min_edge_bps / 10000

        for market in self.market_data:
            yes_price = float(market["yes_price"])
            no_price = float(market["no_price"])
            if yes_price + no_price < threshold:
                signals.append(
                    {
                        "type": "arbitrage",
                        "market": market["id"],
                        "yes_price": yes_price,
                        "no_price": no_price,
                        "size": 25.0,
                    }
                )
        return signals

from strategies.base_strategy import BaseStrategy


class HybridStrategy(BaseStrategy):
    def __init__(self, strategies: list[BaseStrategy]) -> None:
        super().__init__()
        self.strategies = strategies

    def on_market_update(self, market_data: list[dict]) -> None:
        super().on_market_update(market_data)
        for s in self.strategies:
            s.on_market_update(market_data)

    def tune_from_pnl(self, daily_pnl: float) -> None:
        for s in self.strategies:
            s.tune_from_pnl(daily_pnl)

    def generate_signals(self) -> list[dict]:
        out: list[dict] = []
        for s in self.strategies:
            out.extend(s.generate_signals())
        return out

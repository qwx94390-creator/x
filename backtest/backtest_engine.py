class BacktestEngine:
    def __init__(self, strategy, market_data: list[dict]) -> None:
        self.strategy = strategy
        self.market_data = market_data

    def run(self) -> list[dict]:
        all_signals: list[dict] = []
        for tick in self.market_data:
            self.strategy.on_market_update([tick])
            all_signals.extend(self.strategy.generate_signals())
        return all_signals

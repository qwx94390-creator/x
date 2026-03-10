from strategies.base_strategy import BaseStrategy


class MarketMakingStrategy(BaseStrategy):
    def generate_signals(self) -> list[dict]:
        return []

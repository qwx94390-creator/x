from abc import ABC, abstractmethod


class BaseStrategy(ABC):
    def __init__(self) -> None:
        self.market_data: list[dict] = []

    def on_market_update(self, market_data: list[dict]) -> None:
        self.market_data = market_data

    def tune_from_pnl(self, daily_pnl: float) -> None:
        _ = daily_pnl

    @abstractmethod
    def generate_signals(self) -> list[dict]:
        raise NotImplementedError

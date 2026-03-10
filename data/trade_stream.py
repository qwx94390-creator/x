class TradeStream:
    def __init__(self) -> None:
        self.trades: list[dict] = []

    def add_trade(self, trade: dict) -> None:
        self.trades.append(trade)
        if len(self.trades) > 5000:
            self.trades.pop(0)

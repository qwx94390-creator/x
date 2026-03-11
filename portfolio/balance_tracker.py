class BalanceTracker:
    def __init__(self, cash: float = 20.0) -> None:
        self.cash = cash

    def apply_pnl(self, pnl: float) -> None:
        self.cash += pnl

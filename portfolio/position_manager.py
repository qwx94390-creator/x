class PositionManager:
    def __init__(self) -> None:
        self.positions: dict[str, float] = {}

    def apply_fill(self, fill: dict) -> None:
        signed = fill["size"] if "buy" in fill["side"] else -fill["size"]
        self.positions[fill["market"]] = self.positions.get(fill["market"], 0.0) + signed

    def notional(self, market: str, price: float) -> float:
        return abs(self.positions.get(market, 0.0) * price)

from portfolio.position_manager import PositionManager


class RiskEngine:
    def __init__(self, max_order_size: float, max_position_notional: float) -> None:
        self.max_order_size = max_order_size
        self.max_position_notional = max_position_notional

    def check_signal(self, signal: dict, positions: PositionManager) -> bool:
        if signal["size"] > self.max_order_size:
            return False
        current_notional = positions.notional(signal["market"], signal["yes_price"])
        projected = current_notional + signal["size"] * signal["yes_price"]
        return projected <= self.max_position_notional

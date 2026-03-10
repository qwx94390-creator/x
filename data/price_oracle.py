class PriceOracle:
    @staticmethod
    def fair_value(yes_price: float, no_price: float) -> float:
        return (yes_price + (1.0 - no_price)) / 2

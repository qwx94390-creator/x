class LiquidationRules:
    def should_liquidate(self, drawdown_pct: float) -> bool:
        return drawdown_pct > 0.2

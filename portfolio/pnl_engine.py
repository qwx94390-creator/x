class PnLEngine:
    @staticmethod
    def unrealized(position: float, mark: float, avg_entry: float) -> float:
        return (mark - avg_entry) * position

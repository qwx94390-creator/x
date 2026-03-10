class TradeAnalysis:
    @staticmethod
    def win_rate(results: list[float]) -> float:
        if not results:
            return 0.0
        return sum(1 for r in results if r > 0) / len(results)

class MetricsCollector:
    def __init__(self) -> None:
        self.fills = 0
        self.volume = 0.0

    def record_fill(self, fill: dict) -> None:
        self.fills += 1
        self.volume += fill["size"] * fill["price"]

    def snapshot(self) -> dict:
        return {"fills": self.fills, "volume": round(self.volume, 4)}

import csv


class HistoricalLoader:
    def load_csv(self, path: str) -> list[dict]:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

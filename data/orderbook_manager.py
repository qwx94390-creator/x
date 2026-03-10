class OrderBookManager:
    def __init__(self) -> None:
        self.books: dict[str, dict] = {}

    def update(self, market_id: str, book: dict) -> None:
        self.books[market_id] = book

    def best_bid_ask(self, market_id: str) -> tuple[float, float]:
        book = self.books.get(market_id, {})
        bids = book.get("bids", [])
        asks = book.get("asks", [])
        best_bid = float(bids[0][0]) if bids else 0.0
        best_ask = float(asks[0][0]) if asks else 1.0
        return best_bid, best_ask

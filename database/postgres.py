import sqlite3


class Database:
    def __init__(self, url: str) -> None:
        self.path = self._normalize_path(url)
        self.conn: sqlite3.Connection | None = None

    @staticmethod
    def _normalize_path(url: str) -> str:
        marker = "sqlite+aiosqlite:///"
        if url.startswith(marker):
            return url[len(marker):]
        if url.startswith("sqlite:///"):
            return url[len("sqlite:///"):]
        return "bot.db"

    async def connect(self) -> None:
        self.conn = sqlite3.connect(self.path)

    async def create_tables(self) -> None:
        assert self.conn is not None
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                market TEXT NOT NULL,
                side TEXT NOT NULL,
                price REAL NOT NULL,
                size REAL NOT NULL,
                ts TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    async def insert_trade(self, trade_data: dict) -> None:
        assert self.conn is not None
        self.conn.execute(
            "INSERT INTO trades (market, side, price, size, ts) VALUES (?, ?, ?, ?, ?)",
            (
                trade_data["market"],
                trade_data["side"],
                trade_data["price"],
                trade_data["size"],
                trade_data["ts"].isoformat(),
            ),
        )
        self.conn.commit()

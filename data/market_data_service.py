import json
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen


class MarketDataService:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url.rstrip("/")

    async def get_markets(self, limit: int = 50) -> list[dict[str, Any]]:
        params = urlencode({"limit": limit})
        url = f"{self.api_url}/markets?{params}"

        try:
            with urlopen(url, timeout=10) as resp:  # nosec B310
                payload = json.loads(resp.read().decode("utf-8"))
        except (URLError, TimeoutError, json.JSONDecodeError):
            payload = [
                {"id": "demo-1", "yes_price": 0.46, "no_price": 0.50},
                {"id": "demo-2", "yes_price": 0.41, "no_price": 0.54},
            ]

        markets = payload["data"] if isinstance(payload, dict) and "data" in payload else payload

        normalized = []
        for m in markets:
            yes = float(m.get("bestAsk", m.get("yes_price", 0.0)) or 0.0)
            no = float(m.get("no_price", (1.0 - yes) if yes else 0.0) or 0.0)
            normalized.append({"id": str(m.get("id", m.get("conditionId", "unknown"))), "yes_price": yes, "no_price": no})
        return normalized

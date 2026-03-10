from typing import Any

import httpx


class MarketDataService:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=10)

    async def get_markets(self, limit: int = 50) -> list[dict[str, Any]]:
        resp = await self._client.get(f"{self.api_url}/markets", params={"limit": limit})
        resp.raise_for_status()
        payload = resp.json()
        if isinstance(payload, dict) and "data" in payload:
            markets = payload["data"]
        else:
            markets = payload

        normalized = []
        for m in markets:
            yes = float(m.get("bestAsk", 0.0) or 0.0)
            no = 1.0 - yes if yes else float(m.get("no_price", 0.0) or 0.0)
            normalized.append({"id": str(m.get("id", m.get("conditionId", "unknown"))), "yes_price": yes, "no_price": no})
        return normalized

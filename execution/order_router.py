from dataclasses import dataclass


@dataclass
class FillResult:
    status: str
    market: str
    side: str
    price: float
    size: float


class PaperOrderRouter:
    async def send(self, order: dict) -> dict:
        return FillResult(
            status="filled",
            market=order["market"],
            side=order["side"],
            price=order["price"],
            size=order["size"],
        ).__dict__

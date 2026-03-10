import json
from dataclasses import dataclass

from execution.clob_client import ClobClient
from execution.wallet_signer import WalletSigner


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


class PolymarketOrderRouter:
    def __init__(self, client: ClobClient, signer: WalletSigner) -> None:
        self.client = client
        self.signer = signer

    async def send(self, order: dict) -> dict:
        payload = {
            "market": order["market"],
            "side": order["side"],
            "price": order["price"],
            "size": order["size"],
        }
        body = json.dumps(payload)
        headers = self.signer.build_auth_headers(method="POST", path="/order", body=body)
        resp = self.client.create_order(payload, headers=headers)

        if not resp.ok:
            return {
                "status": "rejected",
                "market": order["market"],
                "side": order["side"],
                "price": order["price"],
                "size": order["size"],
                "error": resp.error,
            }

        data = resp.data
        return {
            "status": data.get("status", "accepted"),
            "market": data.get("market", order["market"]),
            "side": data.get("side", order["side"]),
            "price": float(data.get("price", order["price"])),
            "size": float(data.get("size", order["size"])),
            "raw": data,
        }

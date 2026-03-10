import asyncio

from execution.order_router import PolymarketOrderRouter


class FakeSigner:
    def build_auth_headers(self, method: str, path: str, body: str = "") -> dict[str, str]:
        return {"X-Test": "1"}


class FakeClient:
    def __init__(self, ok: bool):
        self.ok = ok

    def create_order(self, payload: dict, headers: dict | None = None):
        class Resp:
            pass

        r = Resp()
        r.ok = self.ok
        r.error = "boom" if not self.ok else ""
        r.data = {
            "status": "filled",
            "market": payload["market"],
            "side": payload["side"],
            "price": payload["price"],
            "size": payload["size"],
        }
        return r


def test_polymarket_order_router_send_success():
    router = PolymarketOrderRouter(client=FakeClient(ok=True), signer=FakeSigner())
    out = asyncio.run(router.send({"market": "m1", "side": "buy_yes", "price": 0.4, "size": 5}))
    assert out["status"] == "filled"


def test_polymarket_order_router_send_rejected():
    router = PolymarketOrderRouter(client=FakeClient(ok=False), signer=FakeSigner())
    out = asyncio.run(router.send({"market": "m1", "side": "buy_yes", "price": 0.4, "size": 5}))
    assert out["status"] == "rejected"

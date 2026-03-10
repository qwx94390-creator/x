from execution.order_router import PaperOrderRouter


class ExecutionEngine:
    def __init__(self, order_router: PaperOrderRouter) -> None:
        self.order_router = order_router

    def build_order(self, signal: dict) -> dict:
        return {
            "market": signal["market"],
            "side": "buy_yes",
            "price": signal["yes_price"],
            "size": signal["size"],
        }

    async def execute(self, order: dict) -> dict:
        return await self.order_router.send(order)

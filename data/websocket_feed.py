import asyncio
import json
from collections.abc import Callable

import websockets


class WebSocketFeed:
    def __init__(self, uri: str, on_message: Callable[[dict], None]) -> None:
        self.uri = uri
        self.on_message = on_message

    async def connect(self) -> None:
        async with websockets.connect(self.uri) as ws:
            while True:
                raw = await ws.recv()
                try:
                    self.on_message(json.loads(raw))
                except json.JSONDecodeError:
                    self.on_message({"raw": raw})
                await asyncio.sleep(0)

import asyncio
from collections.abc import Awaitable, Callable


async def every(interval_sec: int, task: Callable[[], Awaitable[None]]) -> None:
    while True:
        await task()
        await asyncio.sleep(interval_sec)

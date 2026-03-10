import asyncio
from collections.abc import Awaitable, Callable


async def retry_async(func: Callable[[], Awaitable], retries: int = 3):
    for i in range(retries):
        try:
            return await func()
        except Exception:
            if i == retries - 1:
                raise
            await asyncio.sleep(0.2 * (i + 1))

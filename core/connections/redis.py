from typing import Any

import redis

from core.connections.base import BaseConnectionChecker


class RedisConnectionChecker(BaseConnectionChecker):
    exceptions = (redis.exceptions.RedisError,)

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self._client = None

    async def client(self) -> Any:
        if not self._client:
            self._client = await redis.asyncio.from_url(self.dsn)  # type: ignore[assignment]
        return self._client

    async def close(self) -> None:
        cl = await self.client()
        await cl.aclose()
        self._client = None

    async def perform_check(self) -> bool:
        cl = await self.client()
        result = await cl.ping()
        return bool(result)

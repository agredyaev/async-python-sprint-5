import asyncpg

from core.connections.base import BaseConnectionChecker


class PostgresConnectionChecker(BaseConnectionChecker):
    exceptions = (asyncpg.exceptions.PostgresError, OSError)

    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self._client = None

    async def client(self) -> asyncpg.Connection:
        if not self._client:
            self._client = await asyncpg.connect(self.dsn)
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.close()
            self._client = None

    async def perform_check(self) -> bool:
        result = await (await self.client()).fetchval("SELECT 1")
        return bool(result)

import httpx

from core.connections.base import BaseConnectionChecker


class AppConnectionChecker(BaseConnectionChecker):
    exceptions = (httpx.ConnectError, httpx.ConnectTimeout)

    def __init__(self, url: str) -> None:
        self.url = url
        self._client = None

    async def client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = httpx.AsyncClient()
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def perform_check(self) -> bool:
        client = await self.client()
        response = await client.get(url=self.url)
        return bool(response.status_code == 200)

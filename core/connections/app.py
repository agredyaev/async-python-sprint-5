import httpx

from core.connections.base import BaseConnectionChecker


class AppConnectionChecker(BaseConnectionChecker):
    exceptions = (httpx.ConnectError, httpx.ConnectTimeout)

    def __init__(self, url: str) -> None:
        self.url = url
        self._client: httpx.AsyncClient | None = None

    async def client(self) -> httpx.AsyncClient:
        if not self._client:
            client = httpx.AsyncClient()
            await client.__aenter__()
            self._client = client
        return self._client

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def perform_check(self) -> bool:
        client = await self.client()
        response = await client.get(url=self.url)
        return bool(response.status_code == 200)

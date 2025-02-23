from minio import Minio
from minio.error import S3Error

from core.connections.base import BaseConnectionChecker


class MinioConnectionChecker(BaseConnectionChecker):
    exceptions = (S3Error, ConnectionError, ValueError)

    def __init__(self, endpoint: str, access_key: str, secret_key: str, secure: bool = False) -> None:  # noqa: FBT002 FBT001
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self._client: Minio | None = None

    async def client(self) -> Minio:
        if not self._client:
            self._client = Minio(
                endpoint=self.endpoint, access_key=self.access_key, secret_key=self.secret_key, secure=self.secure
            )
        return self._client

    async def close(self) -> None:
        self._client = None

    async def perform_check(self) -> bool:
        try:
            client = await self.client()
            buckets = client.list_buckets()
            return bool(buckets) or True
        except S3Error as e:
            if e.code == "AccessDenied":
                return True
            raise

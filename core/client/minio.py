from typing import Protocol

from asyncio import to_thread
from collections.abc import AsyncGenerator
from io import BytesIO

from minio import Minio

from core.database.schemas.minio import ObjectStorageConfig, StorageObject
from core.logging.logger import CoreLogger

logger = CoreLogger.get_logger("minio_client")


class MinioClientError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ObjectStorageProtocol(Protocol):
    async def bucket_exists(self) -> bool: ...
    async def make_bucket(self) -> None: ...
    async def put_object(self, object_name: str, data: BytesIO, length: int) -> str: ...
    async def get_object_stream(self, object_name: str) -> AsyncGenerator[bytes, None]: ...
    async def list_objects(self, prefix: str) -> list[StorageObject]: ...
    async def generate_presigned_url(self, object_name: str, expires: int) -> str: ...
    async def check(self) -> bool: ...


class MinioClient(ObjectStorageProtocol):
    def __init__(self, config: ObjectStorageConfig, default_bucket: str = "files") -> None:
        """
        Initialize the Minio client with the given configuration and default bucket.
        """
        self.config = config
        self.default_bucket = default_bucket
        self._client = Minio(
            endpoint=config.endpoint, access_key=config.access_key, secret_key=config.secret_key, secure=config.secure
        )
        self._part_size = config.part_size

    async def bucket_exists(self) -> bool:
        """
        Check if the default bucket exists.
        """
        try:
            return await to_thread(self._client.bucket_exists, self.default_bucket)
        except MinioClientError as exc:
            logger.exception("Bucket existence check failed for %s", self.default_bucket, exc_info=exc)
            raise

    async def make_bucket(self) -> None:
        """
        Create the default bucket.
        """
        try:
            await to_thread(self._client.make_bucket, self.default_bucket)
        except MinioClientError as exc:
            logger.exception("Bucket creation failed for %s", self.default_bucket, exc_info=exc)
            raise

    async def put_object(self, object_name: str, data: BytesIO, length: int) -> str:
        """
        Upload an object to the default bucket.
        """
        try:
            result = await to_thread(
                self._client.put_object, self.default_bucket, object_name, data, length, part_size=self._part_size
            )
        except MinioClientError as exc:
            logger.exception("Failed to upload object %s", object_name, exc_info=exc)
            raise
        else:
            return result.object_name

    async def get_object_stream(self, object_name: str) -> AsyncGenerator[bytes, None]:
        """
        Retrieve an object stream from the default bucket.
        """

        async def stream_generator() -> AsyncGenerator[bytes, None]:
            try:
                response = await to_thread(self._client.get_object, self.default_bucket, object_name)
            except MinioClientError as exc:
                logger.exception("Failed to get object %s", object_name, exc_info=exc)
                raise
            try:
                while True:
                    chunk = await to_thread(response.read, self._part_size)
                    if not chunk:
                        break
                    yield chunk
            except MinioClientError as exc:
                logger.exception("Error reading object stream for %s", object_name, exc_info=exc)
                raise
            finally:
                response.close()
                response.release_conn()

        return stream_generator()

    async def list_objects(self, prefix: str) -> list[StorageObject]:
        """
        List objects in the default bucket with the given prefix.
        """
        try:
            objects = await to_thread(
                self._client.list_objects, self.default_bucket, prefix=prefix, include_version=True
            )
            return [StorageObject(**obj.__dict__) for obj in objects]
        except MinioClientError as exc:
            logger.exception("Failed to list objects with prefix %s", prefix, exc_info=exc)
            raise

    async def generate_presigned_url(self, object_name: str, expires: int) -> str:
        """
        Generate a presigned URL for an object in the default bucket.
        """
        try:
            return await to_thread(self._client.presigned_get_object, self.default_bucket, object_name, expires=expires)
        except MinioClientError as exc:
            logger.exception("Failed to generate presigned URL for %s", object_name, exc_info=exc)
            raise

    async def check(self) -> bool:
        result = self._client.list_buckets()
        return result is not None

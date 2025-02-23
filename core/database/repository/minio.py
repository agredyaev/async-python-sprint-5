from collections.abc import AsyncGenerator
from datetime import timedelta

from minio import S3Error

from core.client.minio import ObjectStorageProtocol
from core.database.schemas.minio import MinioFile, MinioFileDownload, StorageObject
from core.logging.logger import CoreLogger

logger = CoreLogger.get_logger("minio_repo")


class MinioRepository:
    def __init__(self, storage: ObjectStorageProtocol):
        self._storage = storage

    async def upload_file(self, file: MinioFile) -> str:
        """Upload file to object storage"""

        file.data.seek(0, 2)
        size = file.data.tell()
        file.data.seek(0)

        try:
            return await self._storage.put_object(file.object_name, file.data, size)
        except S3Error as exc:
            logger.exception("Failed to upload file %s", file.object_name, exc_info=exc)
            raise

    async def download_file(self, file: MinioFileDownload) -> AsyncGenerator[bytes, None]:
        """Download file contents from storage"""
        try:
            async for chunk in await self._storage.get_object_stream(file.object_name):
                yield chunk
        except S3Error as exc:
            logger.exception("Failed to download file %s", file.object_name, exc_info=exc)
            raise

    async def list_versions(self, file: MinioFile) -> list[StorageObject]:
        """List all available versions for a file"""

        try:
            objects = await self._storage.list_objects(file.prefix)
            return [obj for obj in objects if obj.object_name.endswith("content")]
        except S3Error as exc:
            logger.exception("Failed to list versions for file %s", file.path, exc_info=exc)
            raise

    async def generate_presigned_url(self, file: MinioFile, expires: timedelta = timedelta(hours=1)) -> str:
        """Generate presigned URL for file access"""
        try:
            return await self._storage.generate_presigned_url(file.object_name, int(expires.total_seconds()))
        except S3Error as exc:
            logger.exception("Failed to generate URL for %s", file.object_name, exc_info=exc)
            raise

    @property
    def storage(self) -> ObjectStorageProtocol:
        return self._storage

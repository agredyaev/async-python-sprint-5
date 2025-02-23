from typing import Any, Protocol

import hashlib
import time

from collections.abc import AsyncGenerator, Awaitable
from datetime import UTC, datetime
from io import BytesIO
from uuid import UUID

from asyncpg.pgproto.pgproto import timedelta
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from core.database.repository.minio import MinioRepository
from core.database.repository.redis import RedisRepository, TokenData
from core.database.schemas.minio import MinioFile, MinioFileDownload
from core.logging.logger import CoreLogger
from core.utils.current_timestamp import get_timestamp
from helpers.raise_error import raise_error
from models.file import File, FileVersion, User
from repositories import FileRepository, FileVersionRepository, UserRepository
from schemas.file import FileCreateData, FileResponse, FileVersionResponse, ListUserFilesResponse, ServiceStatusResponse

logger = CoreLogger.get_logger("file_service")


class FileServiceProtocol(Protocol):
    async def upload(self, file: UploadFile, data: FileCreateData) -> FileResponse: ...
    async def download(self, path: str | UUID) -> AsyncGenerator[bytes, None]: ...
    async def list_files(self, user_id: UUID) -> ListUserFilesResponse: ...
    async def get_revisions(self, path: str | UUID, limit: int) -> list[FileVersionResponse]: ...
    async def get_service_status(self) -> ServiceStatusResponse: ...


class FileService(FileServiceProtocol):
    """Service for working with files."""

    __slots__ = ("db", "file_repo", "file_version_repo", "minio", "redis", "user_repo")

    def __init__(
        self,
        db_session: AsyncSession,
        minio_repo: MinioRepository,
        redis_repo: RedisRepository,
        user_repo: UserRepository,
        file_repo: FileRepository,
        file_version_repo: FileVersionRepository,
    ) -> None:
        self.db = db_session
        self.minio = minio_repo
        self.redis = redis_repo
        self.user_repo = user_repo
        self.file_repo = file_repo
        self.file_version_repo = file_version_repo

    async def _get_or_create_user(self, user_id: UUID) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            user = User(external_user_id=user_id)
            user = await self.user_repo.upsert(user)
        return user

    @staticmethod
    def _calculate_checksum(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    async def upload(self, file: UploadFile, data: FileCreateData) -> FileResponse:
        async with self.db.begin():
            user = await self._get_or_create_user(data.user_id)
            file_data = await file.read()
            checksum = self._calculate_checksum(file_data)

            existing_file = await self.file_version_repo.get_by_path(path=data.path)

            if existing_file:
                new_version_number = existing_file.version + 1
                file_meta = self.file_repo.get(existing_file.file_id)
            else:
                new_version_number = 1
                file_meta = File(name=file.filename, owner_id=user.id, version_id=None)

            version = FileVersion(
                file_id=file_meta.id,
                version=new_version_number,
                checksum=checksum,
                size=len(file_data),
                path=data.path,
                bucket=data.bucket,
            )
            new_version = await self.file_version_repo.upsert(version)
            file_meta.version_id = new_version.id
            file_meta = await self.file_repo.upsert(file_meta)

            await self.minio.upload_file(
                MinioFile(
                    file_id=file_meta.id,
                    version=new_version_number,
                    data=BytesIO(file_data),
                    original_path=data.path,
                    bucket=data.bucket,
                )
            )

            file_response = FileResponse(
                id=file_meta.id,
                name=file_meta.name,
                created_at=get_timestamp(),
                path=new_version.path,
                size=new_version.size,
                is_downloadable=True,
            )
            await self.redis.set(
                TokenData(
                    key=str(file_meta.id),
                    expires=datetime.fromtimestamp(new_version.updated_at, tz=UTC) - get_timestamp(),
                )
            )
            return file_response

    async def download(self, path: str | UUID) -> AsyncGenerator[bytes, None]:
        async def generator() -> AsyncGenerator[bytes, None]:
            if isinstance(path, UUID):
                file_meta, *_ = await self.file_version_repo.get_by_ids([path])
                if not file_meta:
                    raise raise_error(status.HTTP_404_NOT_FOUND, f"File not found: {path}")
            else:
                file_meta = await self.file_version_repo.get_by_path(path)
                if not file_meta:
                    raise raise_error(status.HTTP_404_NOT_FOUND, f"File not found: {path}")

            async for chunk in self.minio.download_file(
                file=MinioFileDownload(
                    file_id=file_meta.file_id, version=file_meta.version, original_path=file_meta.path
                )
            ):
                yield chunk

        return generator()

    async def list_files(self, user_id: UUID) -> ListUserFilesResponse:
        files_meta = await self.file_repo.get_by_owner(owner_id=user_id)
        files = await self.file_version_repo.get_by_ids(ids=[f.version_id for f in files_meta])
        return ListUserFilesResponse(
            user_id=user_id,
            files=[
                FileResponse(id=f.file_id, path=f.path, size=f.size, version=f.version, updated_at=f.updated_at)
                for f in files
            ],
        )

    async def get_revisions(self, path: str | UUID, limit: int = 10) -> list[FileVersionResponse]:
        file_versions = await self.file_version_repo.get_by_path(path, limit=limit)
        if not file_versions:
            raise raise_error(status.HTTP_404_NOT_FOUND, f"File not found: {path}")

        return [
            FileVersionResponse(version=fv.version, hash=fv.checksum, modified_at=fv.updated_at, size=fv.size)
            for fv in file_versions
        ]

    @staticmethod
    async def _ping(coro: Awaitable[Any]) -> float:
        service_start = time.monotonic()
        try:
            await coro
        except Exception as e:
            logger.exception("Ping error: %s", exc_info=e)
            raise
        return (time.monotonic() - service_start) * 1000

    async def get_service_status(self) -> ServiceStatusResponse:
        db_latency = await self._ping(self.db.execute(select(1)))

        cache_latency = await self._ping(self.redis.set(TokenData(key="test", expires=timedelta(seconds=1))))

        storage_latency = await self._ping(self.minio.storage.check())

        return ServiceStatusResponse(
            db_latency_ms=db_latency, cache_latency_ms=cache_latency, storage_latency_ms=storage_latency
        )

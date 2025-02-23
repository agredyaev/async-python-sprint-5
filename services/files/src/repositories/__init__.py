from typing import Annotated, Any

from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from conf.settings import settings
from core.client.minio import MinioClient, ObjectStorageProtocol
from core.database.postgres import get_session
from core.database.repository.minio import MinioRepository
from core.database.repository.redis import RedisRepository
from core.database.schemas.minio import ObjectStorageConfig
from repositories.file import FileRepository, FileVersionRepository
from repositories.user import UserRepository

__all__: list[str] = [
    "FileRepository",
    "FileVersionRepository",
    "UserRepository",
    "get_db_session",
    "get_file_repo",
    "get_file_version_repo",
    "get_minio_repo",
    "get_redis_repo",
    "get_user_repo",
]


async def get_db_session() -> AsyncGenerator[AsyncSession, Any]:
    """Provide unit of work for async database operations."""
    async for session in get_session(dsn=settings.pg.dsn):
        yield session


@lru_cache
def get_user_repo(session: Annotated[AsyncSession, Depends(get_db_session)]) -> UserRepository:
    return UserRepository(session=session)


async def get_redis_repo(request: Request) -> RedisRepository:
    redis = request.app.state.redis
    return RedisRepository(redis=redis)


@lru_cache
def get_file_repo(session: Annotated[AsyncSession, Depends(get_db_session)]) -> FileRepository:
    return FileRepository(session=session)


@lru_cache
def get_file_version_repo(session: Annotated[AsyncSession, Depends(get_db_session)]) -> FileVersionRepository:
    return FileVersionRepository(session=session)


@lru_cache
def get_minio_client() -> MinioClient:
    config = ObjectStorageConfig(
        endpoint=settings.minio.endpoint,
        access_key=settings.minio.root_user,
        secret_key=settings.minio.root_password,
        secure=settings.minio.secure,
    )
    return MinioClient(config=config)


@lru_cache
async def get_minio_repo(storage: Annotated[ObjectStorageProtocol, Depends(get_minio_client)]) -> MinioRepository:
    return MinioRepository(storage=storage)

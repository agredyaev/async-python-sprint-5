from typing import Annotated

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.repository.minio import MinioRepository
from core.database.repository.redis import RedisRepository
from repositories import (
    FileRepository,
    FileVersionRepository,
    UserRepository,
    get_db_session,
    get_file_repo,
    get_file_version_repo,
    get_minio_repo,
    get_redis_repo,
    get_user_repo,
)
from services.file import FileService, FileServiceProtocol


@lru_cache
def get_file_service(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    minio: Annotated[MinioRepository, Depends(get_minio_repo)],
    redis: Annotated[RedisRepository, Depends(get_redis_repo)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
    file_repo: Annotated[FileRepository, Depends(get_file_repo)],
    file_version_repo: Annotated[FileVersionRepository, Depends(get_file_version_repo)],
) -> FileServiceProtocol:
    return FileService(db, minio, redis, user_repo, file_repo, file_version_repo)

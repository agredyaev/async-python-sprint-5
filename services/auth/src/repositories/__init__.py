from typing import Annotated, Any

from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from conf.settings import settings
from core.database.postgres import get_session
from core.database.repository.redis import RedisRepository
from repositories.user import UserRepository


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

from typing import Annotated

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from conf.settings import settings
from core.database.uow import AsyncUnitOfWork, UnitOfWorkProtocol
from repositories.user import UserRepository


@lru_cache
def get_uow() -> UnitOfWorkProtocol:
    """Provide unit of work for async database operations."""
    async_engine = create_async_engine(url=settings.pg.dsn, echo=settings.pg.echo_sql_queries, future=True)
    async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    return AsyncUnitOfWork(session_factory=async_session)


@lru_cache
def get_user_repo(uow: Annotated[AsyncUnitOfWork, Depends(get_uow)]) -> UserRepository:
    return UserRepository(uow.session_factory())

import types

from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class UnitOfWorkProtocol(Protocol):
    async def __aenter__(self) -> "AsyncUnitOfWork": ...
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None: ...


class AsyncUnitOfWork(UnitOfWorkProtocol):
    """Unit of work for async database operations."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "AsyncUnitOfWork":
        self.session = self.session_factory()
        await self.session.begin()
        return self

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_val: BaseException | None, exc_tb: types.TracebackType | None
    ) -> None:
        if self.session is not None:
            if exc_type:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()

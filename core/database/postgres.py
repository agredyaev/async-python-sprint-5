from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.logging.logger import CoreLogger

logger = CoreLogger.get_logger("postgres_session")


async def get_session(dsn: str) -> AsyncGenerator[AsyncSession, None]:
    """Get a session for database operations"""
    async_engine = create_async_engine(url=dsn, echo=True)
    async_session = async_sessionmaker(bind=async_engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)

    async with async_session() as session, session.begin():
        try:
            yield session
            await session.commit()
        except SQLAlchemyError as e:
            await session.rollback()
            logger.exception(msg="Database error", exc_info=e)
            raise
        finally:
            await session.close()

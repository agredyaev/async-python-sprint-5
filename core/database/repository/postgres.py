from typing import Any, TypeVar

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import SelectBase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from core.database.repository.protocol import RepositoryProtocol

T = TypeVar("T", bound=Any)
P = TypeVar("P", bound=Any)


class BaseRepository(RepositoryProtocol[T, P]):
    __slots__ = ("session",)

    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def upsert(self, obj: T) -> P:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def get(self, obj: UUID) -> P | None:
        return await self.session.get(self.model, obj)

    async def get_all(self, statement: SelectBase | None) -> Sequence[P]:
        if statement is None:
            statement = select(self.model)

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_by_statement(self, statement: SelectBase | None) -> P | None:
        if statement is None:
            return None
        result = await self.session.execute(statement)
        return result.scalar()

    async def delete(self, obj: T) -> None:
        obj = await self.session.get(self.model, obj)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()

    async def bulk_create(self, objects: Sequence[T]) -> None:
        self.session.add_all(objects)
        await self.session.flush()

    async def exists(self, obj: T) -> bool:
        obj = await self.session.get(self.model, obj)
        return bool(obj)

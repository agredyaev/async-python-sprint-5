from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from core.database.repository.postgres import BaseRepository
from models import Url


class UrlRepository(BaseRepository[Url, Url]):
    model = Url

    async def get_by_short_id(self, short_id: str) -> Url | None:
        stmt = select(self.model).where(self.model.short_id == short_id)
        return await self.get_by_statement(stmt)

    async def get_active_urls(self, user_id: UUID | None = None) -> Sequence[Url]:
        stmt = select(self.model).where(
            self.model.is_deleted is False and self.model.user_id == user_id if user_id else True
        )
        return await self.get_all(stmt)

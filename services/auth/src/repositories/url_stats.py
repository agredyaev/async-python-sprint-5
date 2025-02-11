from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from core.database.repository.postgres import BaseRepository
from core.utils.current_timestamp import get_timestamp
from models import UrlStats


class UrlStatsRepository(BaseRepository[UrlStats, UrlStats]):
    model = UrlStats

    async def get_stats_by_url_id(self, url_id: UUID, limit: int = 10, offset: int = 0) -> Sequence[UrlStats]:
        stmt = (
            select(self.model)
            .where(self.model.url_id == url_id)
            .order_by(self.model.accessed_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return await self.get_all(stmt)

    async def add_visit(self, url_id: UUID, client_info: str | None = None) -> UrlStats:
        stats = UrlStats(url_id=url_id, accessed_at=get_timestamp(), client_info=client_info)
        return await self.upsert(stats)

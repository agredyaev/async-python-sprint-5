from collections.abc import Sequence
from uuid import UUID

from fastapi import Request, status

from core.database.uow import AsyncUnitOfWork
from helpers.raise_error import raise_error
from models import Url
from repositories import UrlRepository, UrlStatsRepository
from schemas.url import (
    UrlCreate,
    URLOriginalGet,
    URLOriginalResponse,
    UrlResponse,
    UrlStatsReq,
    UrlStatsResponse,
    UrlVisibilityUpdate,
)


class UrlService:
    """URL service class."""

    __slots__ = ("_stats_repo", "_uow", "_url_repo")

    def __init__(self, url_repo: UrlRepository, stats_repo: UrlStatsRepository, uow: AsyncUnitOfWork):
        self._url_repo = url_repo
        self._stats_repo = stats_repo
        self._uow = uow

    async def create_url(self, url_data: UrlCreate) -> UrlResponse:
        async with self._uow:
            url = Url(**url_data.model_dump())
            url = await self._url_repo.upsert(url)
            return UrlResponse.model_validate(url)

    @staticmethod
    async def _check_url(url: Url) -> None:
        if not url or url.is_deleted:
            raise_error(status_code=status.HTTP_404_NOT_FOUND, detail="URL not found or deleted")

    async def get_url(self, url_data: URLOriginalGet, request: Request) -> URLOriginalResponse:
        async with self._uow:
            url = await self._url_repo.get_by_short_id(url_data.short_id)
            await self._check_url(url)
            await self._stats_repo.add_visit(url_id=url.id, client_info=request.headers.get("User-Agent"))
            return URLOriginalResponse(original_url=url.original_url)

    async def update_visibility(self, url_data: UrlVisibilityUpdate) -> UrlResponse:
        async with self._uow:
            url = await self._url_repo.get_by_short_id(url_data.short_id)
            await self._check_url(url)
            url.visibility = url_data.visibility
            url = await self._url_repo.upsert(url)
            return UrlResponse.model_validate(url)

    async def get_user_urls(self, user_id: UUID) -> Sequence[UrlResponse]:
        async with self._uow:
            urls = await self._url_repo.get_active_urls(user_id)
            return [UrlResponse.model_validate(url) for url in urls]

    async def get_url_stats(self, url_data: UrlStatsReq) -> UrlStatsResponse:
        async with self._uow:
            url = await self._url_repo.get_by_short_id(url_data.short_id)
            await self._check_url(url)
            stats = await self._stats_repo.get_stats_by_url_id(url.id, url_data.max_results, url_data.offset)
            total = len(stats)

            return UrlStatsResponse(
                total_clicks=total,
                access_time=[s.accessed_at for s in stats],
                client_info=[s.client_info for s in stats] if url_data.full_info else None,
            )

from typing import Annotated

from datetime import datetime
from enum import IntEnum, StrEnum, auto
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from pydantic.functional_serializers import PlainSerializer

FancyUrl = Annotated[HttpUrl, PlainSerializer(lambda x: str(x), return_type=str)]


class UrlVisibility(StrEnum):
    public = auto()
    private = auto()


class UrlStatsInfo(IntEnum):
    full = 1
    short = 2


class UserIdMixIn(BaseModel):
    user_id: UUID | None = Field(default=None, description="User ID from JWT")


class VisibilityMixIn(BaseModel):
    visibility: UrlVisibility


class ShortUrlIdMixIn(BaseModel):
    short_id: str = Field(..., description="Short URL ID")


class OriginalUrlMixIn(BaseModel):
    original_url: FancyUrl = Field(..., description="Original URL to shorten")

    model_config = ConfigDict(from_attributes=True)


class UrlCreate(VisibilityMixIn, OriginalUrlMixIn, UserIdMixIn): ...


class UrlResponse(VisibilityMixIn, ShortUrlIdMixIn, OriginalUrlMixIn):
    model_config = ConfigDict(from_attributes=True)


class UrlStatsResponse(BaseModel):
    total_clicks: int
    access_time: list[datetime]
    client_info: list[str] | None

    model_config = ConfigDict(from_attributes=True)


class URLOriginalGet(ShortUrlIdMixIn): ...


class URLOriginalResponse(OriginalUrlMixIn): ...


class UrlStatsParams(BaseModel):
    full_info: UrlStatsInfo = UrlStatsInfo.short
    max_results: int = 10
    offset: int = 0


class UrlStatsReq(UrlStatsParams, ShortUrlIdMixIn): ...


class UrlVisibilityUpdate(ShortUrlIdMixIn, VisibilityMixIn): ...

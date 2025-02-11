from uuid import UUID

import shortuuid

from sqlalchemy.orm import Mapped, mapped_column

from core.database.models.base import STR_10, STR_512, Base
from core.database.models.mixins import AccessedAtMixin, CreatedAtMixin, IdMixin, UpdatedAtMixin
from schemas.url import UrlVisibility


class Url(Base, IdMixin, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "url"

    original_url: Mapped[STR_512] = mapped_column(nullable=False)
    short_id: Mapped[STR_10] = mapped_column(
        default=lambda: shortuuid.ShortUUID().random(length=8), unique=True, index=True
    )
    is_deleted: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[UUID | None] = mapped_column(nullable=True)
    visibility: Mapped[UrlVisibility] = mapped_column(default=False)


class UrlStats(Base, IdMixin, AccessedAtMixin):
    __tablename__ = "url_stats"
    url_id: Mapped[UUID] = mapped_column(nullable=False)
    client_info: Mapped[STR_512] = mapped_column(nullable=True)

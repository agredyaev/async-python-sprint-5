from uuid import UUID, uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models.base import DATETIME_WITH_TIMEZONE, STR_255
from core.utils.current_timestamp import get_timestamp


class BaseMixin:
    __slots__ = ()
    __abstract__ = True


class IdMixin(BaseMixin):
    """Mixin that adds a UUID primary key field to a model."""

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, nullable=False)


class CreatedAtMixin(BaseMixin):
    """Mixin that adds a timestamp field to a model."""

    created_at: Mapped[DATETIME_WITH_TIMEZONE] = mapped_column(default=get_timestamp, nullable=False)


class AccessedAtMixin(BaseMixin):
    """Mixin that adds a timestamp field to a model."""

    accessed_at: Mapped[DATETIME_WITH_TIMEZONE] = mapped_column(default=get_timestamp, nullable=False)


class UpdatedAtMixin(BaseMixin):
    """Mixin that adds a timestamp field to a model."""

    updated_at: Mapped[DATETIME_WITH_TIMEZONE] = mapped_column(
        default=get_timestamp, onupdate=get_timestamp, nullable=False
    )


class UserIdMixin(BaseMixin):
    """Mixin that adds a UUID primary key field to a model."""

    user_id: Mapped[UUID] = mapped_column(ForeignKey(column="user.id", ondelete="CASCADE"), nullable=False)


class NameMixin:
    """Mixin that adds a name field to a model."""

    name: Mapped[STR_255] = mapped_column(nullable=False)


class DescriptionMixin:
    """Mixin that adds a description field to a model."""

    description: Mapped[STR_255] = mapped_column(nullable=True)


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    """Mixin that adds a timestamp field to a model."""


class IsDeletedMixin(BaseMixin):
    """Mixin that adds a is_deleted field to a model."""

    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)

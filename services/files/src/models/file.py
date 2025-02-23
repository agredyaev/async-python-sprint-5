from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models.base import INT_64, STR_50, STR_512, STR_1024, UUID_PK, Base
from core.database.models.mixins import IdMixin, IsDeletedMixin, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "user"
    __table_args__ = (Index("ix_user_created_at", "created_at"),)
    external_user_id: Mapped[UUID_PK]


class File(Base, IdMixin, TimestampMixin):
    __tablename__ = "file"
    __table_args__ = (Index("ix_file_owner_ver", "owner_id", "version_id"), Index("ix_file_name_trgm", "name"))
    name: Mapped[STR_512] = mapped_column(nullable=False, index=True)
    owner_id: Mapped[UUID] = mapped_column(
        ForeignKey(column="user.external_user_id", ondelete="CASCADE"), nullable=False, index=True
    )
    version_id: Mapped[UUID] = mapped_column(nullable=True, index=True)


class FileVersion(Base, IdMixin, TimestampMixin, IsDeletedMixin):
    __tablename__ = "file_version"
    __table_args__ = (
        CheckConstraint("version > 0", name="version_positive"),
        CheckConstraint("octet_length(checksum) = 64", name="checksum_length"),
        Index("ix_file_version", "file_id", "version", unique=True),
        Index("ix_filev_checksum", "checksum", postgresql_using="hash"),
        Index("ix_filev_size", "size"),
    )
    file_id: Mapped[UUID] = mapped_column(ForeignKey(column="file.id", ondelete="CASCADE"), nullable=False, index=True)
    version: Mapped[INT_64] = mapped_column(default=1, nullable=False, index=True)
    size: Mapped[INT_64] = mapped_column(nullable=False)
    checksum: Mapped[STR_1024] = mapped_column(nullable=False, index=True)
    path: Mapped[STR_1024] = mapped_column(nullable=False, index=True)
    bucket: Mapped[STR_50] = mapped_column(nullable=False)

    @property
    def s3_uri(self) -> str:
        return f"s3://{self.bucket}/{self.path}"

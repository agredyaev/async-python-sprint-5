from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from core.database.repository.postgres import BaseRepository
from models import File, FileVersion


class FileRepository(BaseRepository[File, File]):
    """Repository for working with files."""

    model = File

    async def get_by_owner(self, owner_id: UUID) -> Sequence[File]:
        stmt = select(self.model).where(self.model.owner_id == owner_id and self.model.is_deleted is False)
        return await self.get_all(stmt)

    async def get_by_checksum(self, checksum: str) -> File | None:
        stmt = (
            select(self.model)
            .join(FileVersion)
            .where(FileVersion.checksum == checksum and FileVersion.is_deleted is False)
        )
        return await self.get_by_statement(stmt)


class FileVersionRepository(BaseRepository[FileVersion, FileVersion]):
    """Repository for working with file versions."""

    model = FileVersion

    async def get_current_version(self, file_id: UUID) -> FileVersion | None:
        stmt = (
            select(self.model)
            .where(self.model.file_id == file_id and self.model.is_deleted is False)
            .order_by(self.model.version.desc())
            .limit(1)
        )
        return await self.get_by_statement(stmt)

    async def get_versions(self, file_id: UUID) -> Sequence[FileVersion]:
        stmt = (
            select(self.model)
            .where(self.model.file_id == file_id and self.model.is_deleted is False)
            .order_by(self.model.version)
        )
        return await self.get_all(stmt)

    async def get_by_path(self, path: str, limit: int = 1) -> FileVersion | None | Sequence[FileVersion]:
        stmt = (
            select(self.model)
            .where(self.model.path == path and self.model.is_deleted is False)
            .order_by(self.model.version.desc())
        )
        if limit == 1:
            stmt = stmt.limit(1)
            return await self.get_by_statement(stmt)
        return await self.get_all(stmt.limit(limit))

    async def get_by_ids(self, ids: Sequence[UUID]) -> Sequence[FileVersion]:
        stmt = select(self.model).where(self.model.id.in_(ids).order_by(self.model.version.desc()))
        return await self.get_all(stmt)

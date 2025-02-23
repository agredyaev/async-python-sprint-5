from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select

from core.database.repository.postgres import BaseRepository
from models.file import User


class UserRepository(BaseRepository[User, User]):
    """User repository."""

    model = User

    async def get_by_external_id(self, external_id: UUID) -> User | None:
        stmt = select(self.model).where(self.model.external_user_id == external_id)
        return await self.get_by_statement(stmt)

    async def get_active_users(self) -> Sequence[User]:
        stmt = select(self.model).where(self.model.is_deleted is False)
        return await self.get_all(stmt)

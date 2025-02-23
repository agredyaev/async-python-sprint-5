from collections.abc import Sequence

from sqlalchemy import select

from core.database.repository.postgres import BaseRepository
from models import User


class UserRepository(BaseRepository[User, User]):
    model = User

    async def get_by_username(self, username: str) -> User | None:
        stmt = select(self.model).where(self.model.username == username)
        return await self.get_by_statement(stmt)

    async def get_active_users(self) -> Sequence[User]:
        stmt = select(self.model).where(self.model.is_active is True)
        return await self.get_all(stmt)

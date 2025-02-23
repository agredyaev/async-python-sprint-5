from sqlalchemy.orm import Mapped, mapped_column

from core.database.models.base import STR_50, STR_512, Base
from core.database.models.mixins import CreatedAtMixin, IdMixin


class User(Base, CreatedAtMixin, IdMixin):
    __tablename__ = "user"

    username: Mapped[STR_50] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[STR_512] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)

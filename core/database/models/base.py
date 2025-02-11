from typing import Annotated, Any, ClassVar

from datetime import datetime

from sqlalchemy import TIMESTAMP, String
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column

STR_512 = Annotated[str, 512]
STR_255 = Annotated[str, 255]
STR_50 = Annotated[str, 50]
STR_10 = Annotated[str, 10]
DATETIME_WITH_TIMEZONE = Annotated[datetime, mapped_column(TIMESTAMP(timezone=True))]


class Base(AsyncAttrs, DeclarativeBase):
    """Base model class"""

    type_annotations_map: ClassVar[dict[type[Any], Any]] = {
        STR_10: String(10),
        STR_50: String(50),
        STR_255: String(255),
        STR_512: String(512),
    }

    def __repr__(self) -> str:
        class_attrs = ", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({class_attrs})"

from datetime import datetime
from uuid import UUID

from passlib.hash import bcrypt
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator


class UserCredentialsMixin(BaseModel):
    username: str = Field(..., min_length=5, description="Username must be at least 5 characters")
    password: str = Field(
        ...,
        min_length=8,
        description="Password must be at least 8 characters. Hashed during validation",
        alias="hashed_password",
    )


class UserCreate(UserCredentialsMixin):
    """User creation model."""

    @field_validator("password", mode="before")
    @classmethod
    def hash_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValidationError("Password must be at least 8 characters")
        return bcrypt.hash(v)


class UserAuth(UserCredentialsMixin):
    """User authentication model."""

    def verify_password(self, hashed_password: str) -> bool:
        return bcrypt.verify(self.password, hashed_password)


class UserResponse(BaseModel):
    id: UUID
    username: str
    hashed_password: str = Field(exclude=True)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserTokenGen(BaseModel):
    user_id: UUID

    model_config = ConfigDict(from_attributes=True)


class UserLogoutResponse(BaseModel):
    detail: str = "Successfully logged out"
    model_config = ConfigDict(from_attributes=True)

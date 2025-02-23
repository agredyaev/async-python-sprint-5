from typing import Any

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserId(BaseModel):
    user_id: UUID = Field(..., description="User ID")

    model_config = ConfigDict(from_attributes=True)


class UserTokenGenData(BaseModel):
    access_token: dict[str, Any] = Field(..., description="Access token")
    refresh_token: dict[str, Any] = Field(..., description="Refresh token")

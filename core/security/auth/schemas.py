from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UserId(BaseModel):
    user_id: UUID = Field(..., description="User ID")

    model_config = ConfigDict(from_attributes=True)

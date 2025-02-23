from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FileResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
    path: str
    size: int
    version: int
    is_downloadable: bool


class ListUserFilesResponse(BaseModel):
    user_id: UUID
    files: list[FileResponse]

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)


class FileCreateData(BaseModel):
    path: str = Field(..., min_length=1, description="File path on storage")
    user_id: UUID = Field(..., description="User ID of the file owner")
    bucket: str = Field(..., min_length=1, description="Storage bucket")


class FileVersion(BaseModel):
    version: int
    hash: str
    modified_at: datetime
    size: int


class FileMetadata(BaseModel):
    id: UUID
    path: str
    size: int
    hash: str
    version: int = 1
    created_at: datetime
    modified_at: datetime
    owner_id: UUID


class ServiceStatusResponse(BaseModel):
    db_latency_ms: float
    cache_latency_ms: float
    storage_latency_ms: float
    status: str = "healthy"


class FileVersionResponse(BaseModel):
    version: int
    hash: str
    size: int
    modified_at: datetime

    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

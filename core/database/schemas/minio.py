from io import BytesIO
from urllib.parse import unquote
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field


class ObjectStorageConfig(BaseModel):
    endpoint: str
    access_key: str
    secret_key: str
    secure: bool = False
    part_size: int = 50 * 1024 * 1024


class DataMixin(BaseModel):
    data: BytesIO

    model_config = ConfigDict(arbitrary_types_allowed=True)


class StorageObjectFile(BaseModel):
    file_id: UUID
    version: int
    original_path: str
    bucket: str = Field(default="files")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def path(self) -> str:
        return unquote(self.original_path).strip("/")

    @computed_field  # type: ignore[prop-decorator]
    @property
    def object_name(self) -> str:
        return f"{self.path}/v{self.version}/content"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def prefix(self) -> str:
        return f"{self.original_path}/"


class MinioFile(StorageObjectFile, DataMixin): ...


class MinioFileDownload(StorageObjectFile): ...


class StorageObject(BaseModel):
    object_name: str
    version_id: str
    last_modified: str
    size: int

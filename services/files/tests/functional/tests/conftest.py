import uuid
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

USER_ID = uuid.uuid4()


@pytest.fixture
def test_user_id():
    return USER_ID


@pytest.fixture(scope="session")
def app():
    from main import app

    async def mock_auth_middleware(request, call_next):
        request.state.user_id = USER_ID
        request.state.jti = "test_jti"
        return await call_next(request)

    app.middleware_stack = None
    app.user_middleware = []

    app.middleware("http")(mock_auth_middleware)

    return app


@pytest.fixture(scope="module")
def client(app: FastAPI):
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def mock_dependencies(mocker):
    mock_redis = AsyncMock()
    mock_redis.exists.return_value = False
    mock_redis.set.return_value = True
    mocker.patch("core.database.repository.redis.get_redis_client", return_value=mock_redis)

    mock_session = AsyncMock(spec=AsyncSession)
    mocker.patch("core.database.postgres.get_session", return_value=mock_session)

    mock_storage = AsyncMock()
    mock_storage.check = AsyncMock(return_value=True)
    mock_storage.bucket_exists = AsyncMock(return_value=True)
    mock_storage.put_object = AsyncMock(return_value="test_object_name")
    mock_storage.get_object_stream = AsyncMock(return_value=[b"test content"])
    mock_storage.list_objects = AsyncMock(return_value=[])
    mock_storage.generate_presigned_url = AsyncMock(return_value="test_url")

    mocker.patch("repositories.get_minio_client", return_value=mock_storage)

    mock_minio = MagicMock()
    mock_minio.upload_file = AsyncMock(return_value="test_object")
    mock_minio.download_file = AsyncMock(return_value=[b"test content"])
    mocker.patch("repositories.get_minio_client", return_value=mock_minio)


@pytest.fixture(autouse=True)
def mock_redis_repo(client, mocker):  # type: ignore[no-untyped-def]
    mock = AsyncMock()
    client.app.state.redis = mock
    return mock

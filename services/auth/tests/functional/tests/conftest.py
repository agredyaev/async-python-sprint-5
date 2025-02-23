from typing import Any

from collections.abc import Generator
from unittest.mock import AsyncMock, Mock

import pytest

from faker import Faker
from fastapi.testclient import TestClient

from main import app


fake = Faker()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, Any, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def random_user_data() -> dict[str, str]:
    return {
        "username": fake.user_name() + str(fake.random_int()),
        "hashed_password": fake.password(length=12, special_chars=True),
    }


@pytest.fixture(autouse=True)
def mock_redis_repo(client, mocker):  # type: ignore[no-untyped-def]
    mock = AsyncMock()
    client.app.state.redis = mock
    return mock

from typing import Any

from collections.abc import Generator
from unittest.mock import Mock, patch

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


@pytest.mark.asyncio
async def test_signup(client: TestClient, mocker, random_user_data) -> None:  # type: ignore[no-untyped-def]
    mock_client = Mock()
    mock_client.host = "127.0.0.4"
    mocker.patch("starlette.requests.Request.client", new_callable=lambda: mock_client)

    signup_response = client.post("/api/v1/user/signup", json=random_user_data)
    assert signup_response.is_success, "Signup failed"
    user_name = signup_response.json()["username"]
    assert user_name == random_user_data["username"], "Username does not match"

    second_signup_response = client.post("/api/v1/user/signup", json=random_user_data)
    assert second_signup_response.status_code == 409, "Signup succeeded when it should have failed (409)"


@pytest.mark.asyncio
async def test_login(client: TestClient, mocker, random_user_data) -> None:  # type: ignore[no-untyped-def]
    mock_client = Mock()
    mock_client.host = "127.0.0.4"
    mocker.patch("starlette.requests.Request.client", new_callable=lambda: mock_client)

    login_response = client.post("/api/v1/user/login", json=random_user_data)
    assert login_response.is_success, "Login failed"
    user_name = login_response.json()["username"]
    assert user_name == random_user_data["username"], "Username does not match"
    access_token = login_response.cookies["access_token"]

    assert access_token, "Access token not found"


@pytest.mark.asyncio
async def test_logout(client: TestClient, mocker, random_user_data) -> None:  # type: ignore[no-untyped-def]
    mock_client = Mock()
    mock_client.host = "127.0.0.4"
    mocker.patch("starlette.requests.Request.client", new_callable=lambda: mock_client)
    login_response = client.post("/api/v1/user/login", json=random_user_data)
    assert login_response.is_success, "Login failed"

    logout_response = client.post(
        "/api/v1/user/logout", headers={"Authorization": f"Bearer {login_response.cookies['access_token']}"}
    )
    assert logout_response.is_success, "Logout failed"

    access_token = login_response.cookies["access_token"]
    assert access_token == "", "Access token not cleared"

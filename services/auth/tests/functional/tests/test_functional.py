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
async def test_flow(client: TestClient, mocker, random_user_data) -> None:  # type: ignore[no-untyped-def]
    mock_client = Mock()
    mock_client.host = "127.0.0.4"
    mocker.patch("starlette.requests.Request.client", new_callable=lambda: mock_client)

    signup_response = client.post("/api/v1/user/signup", json=random_user_data)
    assert signup_response.is_success, "Signup failed"
    user_name = signup_response.json().get("username")
    assert user_name == random_user_data.get("username"), "Username does not match"

    second_signup_response = client.post("/api/v1/user/signup", json=random_user_data)
    assert second_signup_response.status_code == 409, "Signup succeeded when it should have failed (409)"

    logout_response_signup = client.post(
        "/api/v1/user/logout", headers={"Authorization": f"Bearer {signup_response.cookies['access_token_cookie']}"}
    )
    assert logout_response_signup.is_success, "Logout failed"

    access_token = logout_response_signup.cookies.get("access_token_cookie")
    assert not access_token, "Access token not cleared"

    login_response = client.post("/api/v1/user/login", json=random_user_data)
    assert login_response.is_success, "Login failed"
    user_name = login_response.json().get("username")
    assert user_name == random_user_data.get("username"), "Username does not match"
    access_token = login_response.cookies.get("access_token_cookie")

    assert access_token, "Access token not found"

    logout_response_login = client.post(
        "/api/v1/user/logout", headers={"Authorization": f"Bearer {signup_response.cookies['access_token_cookie']}"}
    )
    assert logout_response_login.is_success, "Logout failed"

    access_token = logout_response_login.cookies.get("access_token_cookie")
    assert not access_token, "Access token not cleared"

from unittest.mock import Mock

import pytest

from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_flow(client: TestClient, mocker, random_user_data, mock_redis_repo) -> None:  # type: ignore[no-untyped-def]
    mock_client = Mock()
    mock_client.host = "127.0.0.4"
    mocker.patch("starlette.requests.Request.client", new_callable=lambda: mock_client)

    signup_response = client.post("/api/v1/user/signup", json=random_user_data)
    assert signup_response.is_success, "Signup failed"
    user_name = signup_response.json().get("username")
    assert user_name == random_user_data.get("username"), "Username does not match"

    second_signup_response = client.post("/api/v1/user/signup", json=random_user_data)
    assert second_signup_response.status_code == 409, "Signup succeeded when it should have failed (409)"

    login_response = client.post("/api/v1/user/login", json=random_user_data)
    assert login_response.is_success, "Login failed"
    user_name = login_response.json().get("username")
    assert user_name == random_user_data.get("username"), "Username does not match"
    login_access_token = login_response.cookies.get("access_token_cookie")
    assert login_access_token, "Access token not found"
    login_refresh_token = login_response.cookies.get("refresh_token_cookie")
    assert login_refresh_token, "Refresh token not found"

    client.cookies.set("access_token_cookie", login_access_token)
    client.cookies.set("refresh_token_cookie", login_refresh_token)
    logout_response_login = client.post("/api/v1/user/logout")

    assert logout_response_login.is_success, "Logout failed"

    assert not logout_response_login.cookies.get("access_token_cookie"), "Access token not cleared"
    assert not logout_response_login.cookies.get("refresh_token_cookie"), "Refresh token not cleared"

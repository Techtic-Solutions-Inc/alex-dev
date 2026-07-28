import httpx

AUTHENTICATE_URL = "/api/v1/user/authenticate"


def test_authenticate_success(client, mock_http_client):
    mock_response = httpx.Response(
        status_code=200,
        json={
            "access_token": "test-access-token",
            "token_type": "Bearer",
            "expires_in": 86400,
            "sub": "auth0|12345",
        },
        request=httpx.Request("POST", "https://example.auth0.com/oauth/token"),
    )
    mock_http_client.post.return_value = mock_response

    response = client.post(
        AUTHENTICATE_URL,
        json={"email": "user@example.com", "password": "secure-password"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["access_token"] == "test-access-token"
    assert body["token_type"] == "Bearer"
    assert body["expires_in"] == 86400
    assert body["redirect_url"] == "/dashboard"
    assert body["email"] == "user@example.com"

    mock_http_client.post.assert_called_once()
    call_kwargs = mock_http_client.post.call_args.kwargs
    assert call_kwargs["json"]["username"] == "user@example.com"
    assert call_kwargs["json"]["password"] == "secure-password"


def test_authenticate_invalid_credentials(client, mock_http_client):
    mock_response = httpx.Response(
        status_code=403,
        json={
            "error": "invalid_grant",
            "error_description": "Wrong email or password.",
        },
        request=httpx.Request("POST", "https://example.auth0.com/oauth/token"),
    )
    mock_http_client.post.return_value = mock_response

    response = client.post(
        AUTHENTICATE_URL,
        json={"email": "user@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    detail = response.json()["detail"]
    assert detail["error"] == "invalid_credentials"
    assert detail["message"] == "Invalid email or password."


def test_authenticate_missing_fields(client):
    response = client.post(AUTHENTICATE_URL, json={"email": "user@example.com"})

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "password" for error in errors)

    response = client.post(AUTHENTICATE_URL, json={"password": "secret"})

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "email" for error in errors)

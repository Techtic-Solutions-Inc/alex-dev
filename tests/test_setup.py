import logging

import jwt
from fastapi.testclient import TestClient

from src.config.settings import settings
from src.db.session import check_database_connection, engine
from src.middlewares.auth import JWTAuthMiddleware
from src.models.user import User
from src.utils.logging_config import configure_logging
from src.utils.security import create_access_token


def test_database_connection() -> None:
    assert check_database_connection() is True
    with engine.connect() as connection:
        assert connection is not None


def test_jwt_middleware(client: TestClient, test_user: User) -> None:
    unauthorized = client.get("/users/me")
    assert unauthorized.status_code == 401
    assert unauthorized.json()["error"]["code"] == "authentication_error"

    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    authorized = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert authorized.status_code == 200
    assert authorized.json()["email"] == test_user.email

    invalid = client.get("/users/me", headers={"Authorization": "Bearer invalid-token"})
    assert invalid.status_code == 401


def test_jwt_middleware_public_paths(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_logging_configuration() -> None:
    configure_logging()
    logger = logging.getLogger("src")
    assert logger.isEnabledFor(logging.INFO)
    assert logging.getLogger("uvicorn").isEnabledFor(logging.INFO)


def test_jwt_middleware_class_instantiation() -> None:
    middleware = JWTAuthMiddleware(app=None)  # type: ignore[arg-type]
    assert middleware is not None


def test_valid_token_payload_decoding(test_user: User) -> None:
    token = create_access_token(data={"sub": str(test_user.id), "email": test_user.email})
    payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    assert payload["sub"] == str(test_user.id)
    assert payload["email"] == test_user.email

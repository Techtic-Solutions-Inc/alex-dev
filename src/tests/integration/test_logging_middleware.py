from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_logging_middleware(client: TestClient) -> None:
    with patch("src.middlewares.logging.logger.info") as mock_logger_info:
        response = client.get("/openapi.json")
        assert response.status_code == 200
        mock_logger_info.assert_called_with(
            "Request: GET /openapi.json - Response: 200"
        )

import pytest
from unittest.mock import patch
from src.middleware.logging_middleware import LoggingMiddleware

@pytest.mark.order(5)
def test_logging_middleware():
    with patch('src.config.logger_config.logger.info') as mock_logger_info:
        middleware = LoggingMiddleware()
        middleware.use({'method': 'GET', 'url': '/test'}, {}, lambda: None)
        mock_logger_info.assert_called_with('Request... GET /test')

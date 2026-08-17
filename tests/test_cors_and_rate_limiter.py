import pytest
from unittest.mock import patch

@pytest.mark.order(7)
def test_cors_configuration():
    with patch('src.main.app.enableCors') as mock_enable_cors:
        mock_enable_cors.assert_called_with({'origin': '*'})

@pytest.mark.order(7)
def test_rate_limiter_configuration():
    from src.middleware.rate_limiter_middleware import rateLimiter
    assert rateLimiter.points == 5
    assert rateLimiter.duration == 1

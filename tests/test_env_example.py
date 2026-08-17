import os
import pytest

@pytest.mark.order(6)
def test_env_example_file():
    required_keys = [
        'DATABASE_URL',
        'JWT_SECRET',
        'JWT_EXPIRY',
        'JWT_REFRESH_EXPIRY',
        'APP_NAME',
        'APP_ENV',
        'DEBUG',
        'API_V1_PREFIX',
        'CORS_ORIGINS',
        'RATE_LIMIT_REQUESTS',
        'RATE_LIMIT_WINDOW_SECONDS'
    ]
    with open('.env.example', 'r') as file:
        content = file.read()
        for key in required_keys:
            assert key in content, f"{key} not found in .env.example"

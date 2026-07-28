import os
import pytest
from src.auth_service import create_access_token

@pytest.fixture
def access_token():
    return create_access_token({'user_id': 1})

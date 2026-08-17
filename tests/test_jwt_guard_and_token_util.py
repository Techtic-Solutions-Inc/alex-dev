import pytest
from unittest.mock import patch
from src.common.utils.token_util import generate_token

@pytest.mark.order(3)
def test_generate_token():
    with patch('src.common.utils.token_util.JwtService') as MockJwtService:
        mock_jwt_service = MockJwtService.return_value
        mock_jwt_service.sign.return_value = 'mocked_token'
        token = generate_token('user_id')
        assert token == 'mocked_token', "Token generation did not return expected value"

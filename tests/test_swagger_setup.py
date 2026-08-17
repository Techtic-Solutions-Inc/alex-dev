import pytest
from unittest.mock import patch

@pytest.mark.order(8)
def test_swagger_setup():
    with patch('src.main.SwaggerModule.setup') as mock_swagger_setup:
        mock_swagger_setup.assert_called_with('api', any, any)

import pytest
from src.common.exceptions.http_exception import HttpException

@pytest.mark.order(4)
def test_http_exception():
    exception = HttpException('Error occurred', 400)
    assert exception.message == 'Error occurred'
    assert exception.status == 400

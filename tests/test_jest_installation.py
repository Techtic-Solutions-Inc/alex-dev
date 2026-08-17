import pytest
import subprocess

@pytest.mark.order(9)
def test_jest_installation():
    result = subprocess.run(['npm', 'list', '--depth=0'], capture_output=True, text=True)
    assert '@nestjs/testing' in result.stdout
    assert 'jest' in result.stdout
    assert 'ts-jest' in result.stdout

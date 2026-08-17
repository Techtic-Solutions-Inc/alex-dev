import pytest
import os

@pytest.mark.order(10)
def test_eslint_prettier_setup():
    assert os.path.exists('.eslintrc.js'), "ESLint config file does not exist"
    with open('.eslintrc.js', 'r') as file:
        content = file.read()
        assert 'plugin:prettier/recommended' in content
        assert 'prettier/prettier' in content

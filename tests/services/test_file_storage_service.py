import pytest
from src.services.file_storage_service import FileStorageService

@pytest.fixture()
def file_storage_service():
    return FileStorageService()

# Happy path test
def test_store_file_happy_path(file_storage_service):
    file_data = b'This is a test file.'
    file_name = 'test_file.txt'
    url = file_storage_service.store_file(file_name, file_data)
    assert url is not None

# Edge case tests
def test_store_file_empty_data(file_storage_service):
    with pytest.raises(ValueError):
        file_storage_service.store_file('empty_file.txt', b'')

def test_store_file_large_data(file_storage_service):
    large_data = b'A' * (10 * 1024 * 1024 + 1)  # 10MB + 1 byte
    with pytest.raises(ValueError):
        file_storage_service.store_file('large_file.txt', large_data)

# Error case tests
def test_store_file_invalid_type(file_storage_service):
    with pytest.raises(TypeError):
        file_storage_service.store_file('test_file.exe', b'This is an executable file.')

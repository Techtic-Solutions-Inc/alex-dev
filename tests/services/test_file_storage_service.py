import pytest
from services.file_storage_service import FileStorageService
from unittest.mock import MagicMock

@pytest.fixture
def file_storage_service():
    return FileStorageService()

def test_store_file_success(file_storage_service, mocker):
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    mock_file.file = MagicMock()
    mocker.patch.object(file_storage_service.s3_client, 'upload_fileobj')
    url = file_storage_service.store_file(mock_file)
    assert url.startswith("https://")

def test_generate_secure_url(file_storage_service, mocker):
    mocker.patch.object(file_storage_service.s3_client, 'generate_presigned_url', return_value="https://example.com/secure_url")
    url = file_storage_service.generate_secure_url("uploads/test.jpg")
    assert url == "https://example.com/secure_url"
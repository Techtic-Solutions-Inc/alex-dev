import pytest
from fastapi.testclient import TestClient
from api.v1.file_upload import router

client = TestClient(router)

@pytest.mark.parametrize("file_type", ["image/jpeg", "image/png"])
def test_file_upload_success(file_type):
    response = client.post("/files/upload", files={"file": ("test.jpg", b"fake image data", file_type)})
    assert response.status_code == 200
    assert "url" in response.json()

@pytest.mark.parametrize("file_type", ["text/plain", "application/pdf"])
def test_file_upload_invalid_type(file_type):
    response = client.post("/files/upload", files={"file": ("test.txt", b"fake text data", file_type)})
    assert response.status_code == 400

def test_file_upload_too_large():
    response = client.post("/files/upload", files={"file": ("large_file.jpg", b"x" * (6 * 1024 * 1024), "image/jpeg")})
    assert response.status_code == 400
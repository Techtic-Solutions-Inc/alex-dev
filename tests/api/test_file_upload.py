import pytest
from fastapi.testclient import TestClient
from src.api.v1.router import app

@pytest.fixture()
def client():
    return TestClient(app)

@pytest.fixture()
def sample_user():
    return {
        'name': 'Test User',
        'email': 'testuser@example.com',
        'password': 'securepassword',
        'role': 'user'
    }

@pytest.fixture()
def sample_file():
    return {'file': ('test_file.txt', b'This is a test file.')}  # Sample file data

# Happy path tests
def test_file_upload_happy_path(client, sample_file):
    response = client.post('/upload', files=sample_file)
    assert response.status_code == 200
    assert 'url' in response.json()

# Edge case tests
def test_file_upload_empty_file(client):
    response = client.post('/upload', files={'file': ('', b'')})
    assert response.status_code == 400

def test_file_upload_large_file(client):
    large_file = {'file': ('large_file.txt', b'A' * (10 * 1024 * 1024 + 1))}  # 10MB + 1 byte
    response = client.post('/upload', files=large_file)
    assert response.status_code == 400

# Error case tests
def test_file_upload_invalid_file_type(client):
    invalid_file = {'file': ('test_file.exe', b'This is an executable file.')}  # Invalid file type
    response = client.post('/upload', files=invalid_file)
    assert response.status_code == 400

# Authentication tests
@pytest.mark.parametrize('token, expected_status', [
    (None, 401),  # No token
    ('invalid_token', 403),  # Invalid token
])
def test_file_upload_authentication(client, sample_file, token, expected_status):
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    response = client.post('/upload', files=sample_file, headers=headers)
    assert response.status_code == expected_status

# Integration tests
def test_file_retrieval(client, sample_file):
    upload_response = client.post('/upload', files=sample_file)
    file_url = upload_response.json()['url']
    retrieval_response = client.get(file_url)
    assert retrieval_response.status_code == 200
    assert retrieval_response.content == b'This is a test file.'

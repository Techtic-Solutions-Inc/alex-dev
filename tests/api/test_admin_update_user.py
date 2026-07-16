import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_admin_update_user_happy_path(async_client: AsyncClient, admin_token, user_id):
    response = await async_client.post('/admin/users/update', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'user_id': user_id,
        'status': 'ACTIVE'
    })
    assert response.status_code == 200
    assert response.json()['message'] == 'User account updated successfully'

@pytest.mark.asyncio
async def test_admin_update_user_edge_case_invalid_status(async_client: AsyncClient, admin_token, user_id):
    response = await async_client.post('/admin/users/update', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'user_id': user_id,
        'status': 'INVALID_STATUS'
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_admin_update_user_edge_case_empty_user_id(async_client: AsyncClient, admin_token):
    response = await async_client.post('/admin/users/update', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'user_id': '',
        'status': 'ACTIVE'
    })
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_admin_update_user_error_case_nonexistent_user(async_client: AsyncClient, admin_token):
    response = await async_client.post('/admin/users/update', headers={'Authorization': f'Bearer {admin_token}'}, json={
        'user_id': 'nonexistent-user-id',
        'status': 'ACTIVE'
    })
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_admin_update_user_auth_missing_token(async_client: AsyncClient, user_id):
    response = await async_client.post('/admin/users/update', json={
        'user_id': user_id,
        'status': 'ACTIVE'
    })
    assert response.status_code == 401
    assert response.json()['detail'] == 'Not authenticated'
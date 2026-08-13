import pytest
from httpx import AsyncClient
from app.models.content import Content

@pytest.mark.asyncio
async def test_create_content(client: AsyncClient, user_auth_header):
    # Test: Create new content
    response = await client.post('/api/content', json={
        'caption': 'New Content',
        'terms_accepted': True,
        'privacy_policy': True,
        'phone': '+1-555-0100'
    }, headers=user_auth_header)
    assert response.status_code == 201
    assert response.json()['caption'] == 'New Content'

@pytest.mark.asyncio
async def test_create_content_missing_fields(client: AsyncClient, user_auth_header):
    # Test: Create content with missing fields
    response = await client.post('/api/content', json={
        'caption': 'Incomplete Content'
    }, headers=user_auth_header)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_create_content_duplicate_caption(client: AsyncClient, user_auth_header, db_session):
    # Setup: Create a content entry
    content = Content(caption='Duplicate Content', phone='+1-555-0100', terms_accepted=True, privacy_policy=True)
    db_session.add(content)
    db_session.commit()

    # Test: Attempt to create duplicate content
    response = await client.post('/api/content', json={
        'caption': 'Duplicate Content',
        'terms_accepted': True,
        'privacy_policy': True,
        'phone': '+1-555-0100'
    }, headers=user_auth_header)
    assert response.status_code == 409

@pytest.mark.asyncio
async def test_get_content_details(client: AsyncClient, db_session):
    # Setup: Create a content entry
    content = Content(caption='Detail Content', phone='+1-555-0100', terms_accepted=True, privacy_policy=True)
    db_session.add(content)
    db_session.commit()

    # Test: Retrieve content details
    response = await client.get(f'/api/content/{content.id}')
    assert response.status_code == 200
    assert response.json()['caption'] == 'Detail Content'

@pytest.mark.asyncio
async def test_update_content_invalid_data(client: AsyncClient, user_auth_header, db_session):
    # Setup: Create a content entry
    content = Content(caption='Update Content', phone='+1-555-0100', terms_accepted=True, privacy_policy=True)
    db_session.add(content)
    db_session.commit()

    # Test: Update content with invalid data
    response = await client.put(f'/api/content/{content.id}', json={
        'caption': ''
    }, headers=user_auth_header)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_content_success(client: AsyncClient, user_auth_header, db_session):
    # Setup: Create a content entry
    content = Content(caption='Update Content', phone='+1-555-0100', terms_accepted=True, privacy_policy=True)
    db_session.add(content)
    db_session.commit()

    # Test: Update content successfully
    response = await client.put(f'/api/content/{content.id}', json={
        'caption': 'Updated Content'
    }, headers=user_auth_header)
    assert response.status_code == 200
    assert response.json()['caption'] == 'Updated Content'

import pytest
from httpx import AsyncClient
from app.models.blog import Blog

@pytest.mark.asyncio
async def test_get_blog_list(client: AsyncClient, db_session):
    # Setup: Create a blog post
    blog = Blog(title='Test Blog', slug='test-blog', content='Test content', phone='+1-555-0100', terms_accepted=True)
    db_session.add(blog)
    db_session.commit()

    # Test: Retrieve blog list
    response = await client.get('/api/blog')
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_create_blog_post(client: AsyncClient, admin_auth_header):
    # Test: Create a new blog post
    response = await client.post('/api/blog', json={
        'title': 'New Blog',
        'content': 'New blog content',
        'terms_accepted': True,
        'phone': '+1-555-0100'
    }, headers=admin_auth_header)
    assert response.status_code == 201
    assert response.json()['title'] == 'New Blog'

@pytest.mark.asyncio
async def test_create_blog_post_missing_fields(client: AsyncClient, admin_auth_header):
    # Test: Create a blog post with missing fields
    response = await client.post('/api/blog', json={
        'title': 'Incomplete Blog'
    }, headers=admin_auth_header)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_update_blog_post(client: AsyncClient, admin_auth_header, db_session):
    # Setup: Create a blog post
    blog = Blog(title='Update Blog', slug='update-blog', content='Content to update', phone='+1-555-0100', terms_accepted=True)
    db_session.add(blog)
    db_session.commit()

    # Test: Update the blog post
    response = await client.put(f'/api/blog/{blog.id}', json={
        'title': 'Updated Blog Title'
    }, headers=admin_auth_header)
    assert response.status_code == 200
    assert response.json()['title'] == 'Updated Blog Title'

@pytest.mark.asyncio
async def test_delete_blog_post(client: AsyncClient, admin_auth_header, db_session):
    # Setup: Create a blog post
    blog = Blog(title='Delete Blog', slug='delete-blog', content='Content to delete', phone='+1-555-0100', terms_accepted=True)
    db_session.add(blog)
    db_session.commit()

    # Test: Delete the blog post
    response = await client.delete(f'/api/blog/{blog.id}', headers=admin_auth_header)
    assert response.status_code == 204

@pytest.mark.asyncio
async def test_get_blog_post_details(client: AsyncClient, db_session):
    # Setup: Create a blog post
    blog = Blog(title='Detail Blog', slug='detail-blog', content='Detailed content', phone='+1-555-0100', terms_accepted=True)
    db_session.add(blog)
    db_session.commit()

    # Test: Retrieve blog post details
    response = await client.get(f'/api/blog/{blog.id}')
    assert response.status_code == 200
    assert response.json()['title'] == 'Detail Blog'

@pytest.mark.asyncio
async def test_get_non_existent_blog_post(client: AsyncClient):
    # Test: Retrieve non-existent blog post
    response = await client.get('/api/blog/999')
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_create_blog_post_without_terms(client: AsyncClient, admin_auth_header):
    # Test: Create a blog post without accepting terms
    response = await client.post('/api/blog', json={
        'title': 'No Terms Blog',
        'content': 'Content without terms',
        'phone': '+1-555-0100'
    }, headers=admin_auth_header)
    assert response.status_code == 400

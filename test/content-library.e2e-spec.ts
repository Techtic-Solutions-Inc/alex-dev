import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Content Library (e2e)', () => {
  let app: INestApplication;
  let authToken: string;
  let userEmail: string;

  const validItem = {
    title: 'Luxury Listing Social Template',
    description: 'Editable social post template designed for luxury property launches and premium brand campaigns.',
    image_url: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
    link: 'https://example.com/content-library/luxury-listing-template',
    category: 'Social Media',
    tags: ['luxury', 'instagram', 'listing'],
    full_name: 'Jane Doe',
    phone: '+1-555-0100',
  };

  beforeAll(async () => {
    app = await createTestApp();
    const auth = await createAuthenticatedUser(app);
    authToken = auth.token;
    userEmail = auth.email;
  });

  afterAll(async () => {
    await clearContentLibraryItems(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearContentLibraryItems(app);
    await setUserRole(app, userEmail, 'agent');
  });

  it('returns 200 with a list of content items', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    const response = await request(app.getHttpServer())
      .get('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content library items retrieved successfully');
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0]).toMatchObject({
      id: created.body.data.id,
      title: validItem.title,
      link: validItem.link,
      description: validItem.description,
      image: validItem.image_url,
      image_url: validItem.image_url,
      category: validItem.category,
      tags: validItem.tags,
      full_name: validItem.full_name,
      phone: validItem.phone,
      error: null,
      is_active: true,
    });
    expect(response.body.data.pagination).toEqual({
      page: 1,
      limit: 10,
      total: 1,
      total_pages: 1,
      has_next_page: false,
      has_previous_page: false,
    });
  });

  it('creates a content item with valid data and returns 201', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem);

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content library item created successfully');
    expect(response.body.data).toMatchObject({
      id: expect.any(String),
      title: validItem.title,
      link: validItem.link,
      description: validItem.description,
      image: validItem.image_url,
      image_url: validItem.image_url,
      category: validItem.category,
      tags: validItem.tags,
      full_name: validItem.full_name,
      phone: validItem.phone,
      error: null,
      is_active: true,
      created_at: expect.any(String),
      updated_at: expect.any(String),
    });
  });

  it('returns 400 with validation details when required create fields are missing', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        description: validItem.description,
        category: validItem.category,
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Validation failed');
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        title: expect.any(Array),
        image_url: expect.any(Array),
        link: expect.any(Array),
        tags: expect.any(Array),
        full_name: expect.any(Array),
        phone: expect.any(Array),
      }),
    );
  });

  it('returns 200 with the requested content item details', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    const response = await request(app.getHttpServer())
      .get(`/api/content-library/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content library item retrieved successfully');
    expect(response.body.data).toMatchObject({
      id: created.body.data.id,
      title: validItem.title,
      link: validItem.link,
      description: validItem.description,
      image: validItem.image_url,
      image_url: validItem.image_url,
      category: validItem.category,
      tags: validItem.tags,
      full_name: validItem.full_name,
      phone: validItem.phone,
      error: null,
    });
  });

  it('updates an existing content item and returns 200', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    const response = await request(app.getHttpServer())
      .put(`/api/content-library/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Luxury Listing Social Template v2',
        category: 'Email Marketing',
        tags: ['newsletter', 'seller'],
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content library item updated successfully');
    expect(response.body.data).toMatchObject({
      id: created.body.data.id,
      title: 'Luxury Listing Social Template v2',
      category: 'Email Marketing',
      tags: ['newsletter', 'seller'],
    });
  });

  it('deletes an existing content item and returns 204', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    const response = await request(app.getHttpServer())
      .delete(`/api/content-library/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(204);
    expect(response.text).toBe('');
  });

  it('returns filtered results from the search endpoint', async () => {
    await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        ...validItem,
        title: 'Open house flyer bundle',
        description: 'Printable flyer pack for weekend open house promotions and neighborhood walkthrough events.',
        category: 'Print',
        image_url: 'https://cdn.example.com/content-library/open-house-flyer.jpg',
        link: 'https://example.com/content-library/open-house-flyer',
        tags: ['flyer', 'print'],
      })
      .expect(201);

    const response = await request(app.getHttpServer())
      .get('/api/content-library/search')
      .query({ q: 'luxury' })
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content library search completed successfully');
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0].title).toBe(validItem.title);
  });

  it('supports query-based filtering on the main list endpoint', async () => {
    await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    await request(app.getHttpServer())
      .post('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        ...validItem,
        title: 'Seller newsletter template',
        category: 'Email Marketing',
        image_url: 'https://cdn.example.com/content-library/seller-newsletter.jpg',
        link: 'https://example.com/content-library/seller-newsletter',
        tags: ['newsletter', 'seller'],
      })
      .expect(201);

    const response = await request(app.getHttpServer())
      .get('/api/content-library')
      .query({ q: 'seller', category: 'Email Marketing' })
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0].title).toBe('Seller newsletter template');
  });

  it('returns 403 when the authenticated user role is not authorized', async () => {
    await setUserRole(app, userEmail, 'viewer');

    const response = await request(app.getHttpServer())
      .get('/api/content-library')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(403);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('CONTENT_LIBRARY_ACCESS_FORBIDDEN');
  });
});

async function createAuthenticatedUser(app: INestApplication): Promise<{ token: string; email: string }> {
  const email = uniqueEmail('content-library.user');
  const password = 'StrongPassword123!';

  await request(app.getHttpServer())
    .post('/api/auth/signup')
    .send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      phone: '+1-555-0100',
      password,
      terms_accepted: true,
    })
    .expect(201);

  const verificationToken = verificationTokens.get(email);
  expect(verificationToken).toBeDefined();

  await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token: verificationToken }).expect(200);

  const loginResponse = await request(app.getHttpServer())
    .post('/api/auth/login')
    .send({ email, password })
    .expect(201);

  return {
    token: loginResponse.body.data.accessToken as string,
    email,
  };
}

async function clearContentLibraryItems(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('content_library_items').deleteMany({});
}

async function setUserRole(app: INestApplication, email: string, role: string): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').updateOne({ email }, { $set: { role } });
}

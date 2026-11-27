import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection, Types } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Real Estate Professional Content Library Search (e2e)', () => {
  let app: INestApplication;
  let userId: string;

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
    userId = auth.userId;
  });

  afterAll(async () => {
    await clearContentLibraryItems(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearContentLibraryItems(app);
  });

  it('returns relevant content items for a valid search query', async () => {
    await seedContentItem(app, userId, validItem);

    const response = await request(app.getHttpServer())
      .get('/api/v1/real-estate-professional/content-library/search')
      .query({ query: 'luxury', full_name: 'Jane Doe', phone: '+1-555-0100' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content library search completed successfully');
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0]).toMatchObject({
      title: validItem.title,
      full_name: validItem.full_name,
      phone: validItem.phone,
      is_active: true,
    });
    expect(response.body.data.pagination.total).toBe(1);
  });

  it('returns 400 when the search query is empty', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/v1/real-estate-professional/content-library/search')
      .query({ query: '   ' });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        query: expect.any(Array),
      }),
    );
  });

  it('returns 404 when no content items match the search query', async () => {
    await seedContentItem(app, userId, validItem);

    const response = await request(app.getHttpServer())
      .get('/api/v1/real-estate-professional/content-library/search')
      .query({ query: 'unicorn-listing-template' });

    expect(response.status).toBe(404);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('CONTENT_LIBRARY_SEARCH_NO_RESULTS');
  });
});

async function createAuthenticatedUser(app: INestApplication): Promise<{ token: string; userId: string }> {
  const email = uniqueEmail('rep-content-library-search');
  const password = 'StrongPassword123!';

  const signup = await request(app.getHttpServer())
    .post('/api/v1/auth/signup')
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

  await request(app.getHttpServer()).get('/api/v1/auth/verify-email').query({ token: verificationToken }).expect(200);

  const loginResponse = await request(app.getHttpServer())
    .post('/api/v1/auth/login')
    .send({ email, password })
    .expect(201);

  return {
    token: loginResponse.body.data.accessToken as string,
    userId: signup.body.data.id as string,
  };
}

interface ContentLibrarySeedItem {
  title: string;
  description: string;
  image_url: string;
  link: string;
  category: string;
  tags: string[];
  full_name: string;
  phone: string;
}

async function seedContentItem(app: INestApplication, ownerUserId: string, item: ContentLibrarySeedItem): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('content_library_items').insertOne({
    user_id: new Types.ObjectId(ownerUserId),
    title: item.title,
    description: item.description,
    image_url: item.image_url,
    link: item.link,
    category: item.category,
    tags: item.tags,
    full_name: item.full_name,
    phone: item.phone,
    is_active: true,
    createdAt: new Date('2026-06-01T10:00:00.000Z'),
    updatedAt: new Date('2026-06-02T12:30:00.000Z'),
  });
}

async function clearContentLibraryItems(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('content_library_items').deleteMany({});
}
import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Real Estate Professional Content (e2e)', () => {
  let app: INestApplication;
  let authToken: string;
  let userEmail: string;

  const validItem = {
    title: 'Hates to see me coming',
    description: 'Trend-ready Instagram caption tailored for local market storytelling.',
    image_url: 'https://cdn.example.com/templates/hates-to-see-me-coming.jpg',
    link: 'https://example.com/templates/hates-to-see-me-coming',
    city: 'Austin',
    tags: ['instagram', 'reel'],
    phone: '+1-555-0100',
    terms_accepted: true,
  };

  beforeAll(async () => {
    app = await createTestApp();
    const auth = await createAuthenticatedUser(app);
    authToken = auth.token;
    userEmail = auth.email;
    await setUserRole(app, userEmail, 'real_estate_professional');
  });

  afterAll(async () => {
    await clearContentItems(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearContentItems(app);
  });

  it('returns 200 with a paginated list without authentication', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    const response = await request(app.getHttpServer()).get('/api/v1/real-estate-professional/content').expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0]).toMatchObject({
      name: validItem.title,
      description: validItem.description,
      city: validItem.city,
      link: validItem.link,
      phone: validItem.phone,
      error: null,
    });
    expect(response.body.data.pagination).toEqual(
      expect.objectContaining({
        page: 1,
        limit: 20,
        total: 1,
        has_next: false,
        has_previous: false,
      }),
    );
  });

  it('creates content and returns 201', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem);

    expect(response.status).toBe(201);
    expect(response.body.data.name).toBe(validItem.title);
    expect(response.body.data.id).toEqual(expect.any(String));
  });

  it('updates content and returns 200', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    const response = await request(app.getHttpServer())
      .put(`/api/v1/real-estate-professional/content/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({ title: 'Instagram Stories', city: 'Denver' });

    expect(response.status).toBe(200);
    expect(response.body.data.name).toBe('Instagram Stories');
    expect(response.body.data.city).toBe('Denver');
  });

  it('deletes content and returns 204', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

  const deleteResponse = await request(app.getHttpServer())
      .delete(`/api/v1/real-estate-professional/content/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(deleteResponse.status).toBe(204);
    expect(deleteResponse.text).toBe('');
  });

  it('returns 400 for empty search term', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/v1/real-estate-professional/content')
      .query({ search: '' });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('EMPTY_SEARCH_TERM');
  });

  it('returns 409 for duplicate content name', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem)
      .expect(201);

    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validItem);

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('CONTENT_ALREADY_EXISTS');
  });

  it('returns 400 when terms_accepted is false', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...validItem, terms_accepted: false });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        terms_accepted: expect.any(Array),
      }),
    );
  });

  it('returns 400 when terms_accepted is omitted', async () => {
    const { terms_accepted: _ignored, ...withoutTerms } = validItem;
    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send(withoutTerms);

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });
});

async function createAuthenticatedUser(app: INestApplication): Promise<{ token: string; email: string }> {
  const email = uniqueEmail('rep.content.user');
  const password = 'StrongPassword123!';

  await request(app.getHttpServer())
    .post('/api/v1/auth/signup')
    .send({
      first_name: 'Alex',
      last_name: 'Agent',
      email,
      phone: '+1-555-0100',
      password,
      terms_accepted: true,
    })
    .expect(201);

  const verificationToken = verificationTokens.get(email);
  await request(app.getHttpServer()).get('/api/v1/auth/verify-email').query({ token: verificationToken }).expect(200);

  const loginResponse = await request(app.getHttpServer())
    .post('/api/v1/auth/login')
    .send({ email, password })
    .expect(201);

  return { token: loginResponse.body.data.accessToken as string, email };
}

async function clearContentItems(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('real_estate_professional_contents').deleteMany({});
}

async function setUserRole(app: INestApplication, email: string, role: string): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').updateOne({ email }, { $set: { role } });
}
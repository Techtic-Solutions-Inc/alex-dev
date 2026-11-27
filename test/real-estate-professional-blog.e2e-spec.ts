import { randomBytes } from 'crypto';
import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

const ephemeralSignupPassword = (): string => `Test-${randomBytes(18).toString('hex')}A!`;

describe('Real Estate Professional Blog (e2e)', () => {
  let app: INestApplication;
  let authToken: string;
  let userEmail: string;

  const validPost = {
    title: 'Hates to see me coming',
    author_email: 'hello@agentwisemarketing.com',
    content: 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.',
    description: 'Insights on local market positioning and social storytelling.',
    image_url: 'https://cdn.example.com/blog/hates-to-see-me-coming.jpg',
    link: 'https://example.com/blog/hates-to-see-me-coming',
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
    await clearBlogPosts(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearBlogPosts(app);
  });

  it('returns 200 with a paginated blog list without authentication', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost)
      .expect(201);

    const response = await request(app.getHttpServer()).get('/api/v1/real-estate-professional/blog').expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0]).toMatchObject({
      title: validPost.title,
      description: validPost.description,
      author_email: validPost.author_email,
      link: validPost.link,
      phone: validPost.phone,
      error: null,
      metadata: expect.objectContaining({
        created_at: expect.any(String),
        updated_at: expect.any(String),
      }),
    });
    expect(response.body.data.pagination.total).toBe(1);
  });

  it('creates a blog post and returns 201', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost);

    expect(response.status).toBe(201);
    expect(response.body.data.title).toBe(validPost.title);
    expect(response.body.data.id).toEqual(expect.any(String));
  });

  it('returns blog details by id when authenticated', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost)
      .expect(201);

    const response = await request(app.getHttpServer())
      .get(`/api/v1/real-estate-professional/blog/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);

    expect(response.body.data).toMatchObject({
      title: validPost.title,
      author_email: validPost.author_email,
      content: validPost.content,
      phone: validPost.phone,
      terms_accepted: true,
      metadata: expect.objectContaining({
        created_at: expect.any(String),
        updated_at: expect.any(String),
      }),
      error: null,
    });
  });

  it('returns 403 for unauthenticated blog detail access', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost)
      .expect(201);

    const response = await request(app.getHttpServer()).get(
      `/api/v1/real-estate-professional/blog/${created.body.data.id}`,
    );

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('BLOG_ACCESS_FORBIDDEN');
  });

  it('returns 404 when blog post does not exist', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/v1/real-estate-professional/blog/66df0b7814b3e891e4ebcd21')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('BLOG_NOT_FOUND');
  });

  it('updates a blog post and returns 200', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost)
      .expect(201);

    const response = await request(app.getHttpServer())
      .put(`/api/v1/real-estate-professional/blog/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({ title: 'Updated blog headline' });

    expect(response.status).toBe(200);
    expect(response.body.data.title).toBe('Updated blog headline');
  });

  it('deletes a blog post and returns 204', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost)
      .expect(201);

    const deleteResponse = await request(app.getHttpServer())
      .delete(`/api/v1/real-estate-professional/blog/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(deleteResponse.status).toBe(204);
    expect(deleteResponse.text).toBe('');
  });

  it('returns 409 for duplicate blog title', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost)
      .expect(201);

    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validPost);

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('BLOG_ALREADY_EXISTS');
  });

  it('returns 400 when title is empty', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...validPost, title: '   ' });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('returns 400 when terms_accepted is false', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...validPost, terms_accepted: false });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('returns 400 when terms_accepted is omitted', async () => {
    const { terms_accepted: _ignored, ...withoutTerms } = validPost;
    const response = await request(app.getHttpServer())
      .post('/api/v1/real-estate-professional/blog')
      .set('Authorization', `Bearer ${authToken}`)
      .send(withoutTerms);

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });
});

async function createAuthenticatedUser(app: INestApplication): Promise<{ token: string; email: string }> {
  const email = uniqueEmail('rep.blog.user');
  const password = ephemeralSignupPassword();

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

async function clearBlogPosts(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('real_estate_professional_blogs').deleteMany({});
}

async function setUserRole(app: INestApplication, email: string, role: string): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').updateOne({ email }, { $set: { role } });
}
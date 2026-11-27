import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { clearUsers, createTestApp, uniqueEmail } from './create-test-app';

describe('Visitor Signup (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createTestApp();
  });

  afterAll(async () => {
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearUsers(app);
  });

  it('registers a visitor and returns 201 with user payload', async () => {
    const email = uniqueEmail('visitor.signup.success');
    const response = await request(app.getHttpServer()).post('/api/v1/visitor/signup').send({
      first_name: 'John',
      last_name: 'Doe',
      email,
      password: 'StrongPassword123!',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data).toMatchObject({
      id: expect.any(String),
      name: 'John Doe',
      first_name: 'John',
      last_name: 'Doe',
      email,
      email_verified: false,
      description: expect.any(String),
      link: expect.any(String),
      error: null,
    });
  });

  it('returns 400 when first name is empty', async () => {
    const response = await request(app.getHttpServer()).post('/api/v1/visitor/signup').send({
      first_name: '   ',
      last_name: 'Doe',
      email: uniqueEmail('visitor.empty-first-name'),
      password: 'StrongPassword123!',
      terms_accepted: true,
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        first_name: expect.arrayContaining([expect.any(String)]),
      }),
    );
  });

  it('returns 400 for invalid email format', async () => {
    const response = await request(app.getHttpServer()).post('/api/v1/visitor/signup').send({
      first_name: 'John',
      last_name: 'Doe',
      email: 'not-an-email',
      password: 'StrongPassword123!',
      terms_accepted: true,
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        email: expect.arrayContaining([expect.any(String)]),
      }),
    );
  });

  it('returns 409 when email is already registered', async () => {
    const email = uniqueEmail('visitor.duplicate');
    const payload = {
      first_name: 'John',
      last_name: 'Doe',
      email,
      password: 'StrongPassword123!',
      terms_accepted: true,
    };

    await request(app.getHttpServer()).post('/api/v1/visitor/signup').send(payload).expect(201);

    const response = await request(app.getHttpServer()).post('/api/v1/visitor/signup').send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      password: 'AnotherStrongPassword123!',
      terms_accepted: true,
    });

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('EMAIL_ALREADY_EXISTS');
  });

  it('returns 400 when terms are not accepted', async () => {
    const response = await request(app.getHttpServer()).post('/api/v1/visitor/signup').send({
      first_name: 'John',
      last_name: 'Doe',
      email: uniqueEmail('visitor.terms'),
      password: 'StrongPassword123!',
      terms_accepted: false,
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        terms_accepted: expect.arrayContaining([expect.any(String)]),
      }),
    );
  });
});
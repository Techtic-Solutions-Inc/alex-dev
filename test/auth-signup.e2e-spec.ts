import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { clearUsers, createTestApp, uniqueEmail } from './create-test-app';

describe('Auth Signup (e2e)', () => {
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

  it('registers a new user successfully', async () => {
    const email = uniqueEmail('signup.success');

    const response = await request(app.getHttpServer()).post('/api/auth/signup').send({
      first_name: 'John',
      last_name: 'Doe',
      email,
      password: 'StrongPassword123!',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body).toEqual({
      success: true,
      message: 'Account created. Please check your email to verify your address.',
      data: {
        id: expect.any(String),
        name: 'John Doe',
        full_name: 'John Doe',
        first_name: 'John',
        last_name: 'Doe',
        email,
        phone: null,
        email_verified: false,
      },
    });
  });

  it('returns validation error when required fields are missing', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/auth/signup')
      .send({
        first_name: 'John',
        email: uniqueEmail('signup.missing'),
        password: 'StrongPassword123!',
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Validation failed');
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: expect.objectContaining({
        last_name: expect.arrayContaining([expect.any(String)]),
        terms_accepted: expect.arrayContaining([expect.any(String)]),
      }),
    });
  });

  it('returns conflict when registering with a duplicate email', async () => {
    const email = uniqueEmail('signup.duplicate');
    const payload = {
      first_name: 'John',
      last_name: 'Doe',
      email,
      password: 'StrongPassword123!',
      terms_accepted: true,
    };

    await request(app.getHttpServer()).post('/api/auth/signup').send(payload).expect(201);

    const response = await request(app.getHttpServer()).post('/api/auth/signup').send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      password: 'AnotherStrongPassword123!',
      terms_accepted: true,
    });

    expect(response.status).toBe(409);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('An account with this email address already exists');
    expect(response.body.error).toEqual({
      code: 'EMAIL_ALREADY_EXISTS',
      details: {
        email: ['An account with this email address already exists'],
      },
    });
  });

  it('returns validation error for a weak password', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/auth/signup')
      .send({
        first_name: 'John',
        last_name: 'Doe',
        email: uniqueEmail('signup.weak'),
        password: 'weak',
        terms_accepted: true,
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        password: [
          'password must be at least 8 characters and include an uppercase letter, number, and special character',
        ],
      },
    });
  });

  it('returns validation error when terms are not accepted', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/auth/signup')
      .send({
        first_name: 'John',
        last_name: 'Doe',
        email: uniqueEmail('signup.terms'),
        password: 'StrongPassword123!',
        terms_accepted: false,
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        terms_accepted: ['terms_accepted must be true'],
      },
    });
  });
});

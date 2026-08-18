import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Auth Login & Session (e2e)', () => {
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

  async function registerVerifiedUser(email: string, password = 'StrongPassword123!'): Promise<void> {
    await request(app.getHttpServer())
      .post('/api/auth/signup')
      .send({
        first_name: 'John',
        last_name: 'Doe',
        email,
        password,
        terms_accepted: true,
      })
      .expect(201);

    const token = verificationTokens.get(email);
    expect(token).toBeDefined();

    await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token }).expect(200);
  }

  it('logs in successfully with valid credentials', async () => {
    const email = uniqueEmail('login.success');
    await registerVerifiedUser(email);

    const response = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Signed in successfully');
    expect(response.body.data).toEqual({
      id: expect.any(String),
      name: 'John Doe',
      full_name: 'John Doe',
      first_name: 'John',
      last_name: 'Doe',
      email,
      phone: null,
      token: expect.any(String),
      accessToken: expect.any(String),
      refreshToken: expect.any(String),
      tokenType: 'Bearer',
    });
  });

  it('returns validation error for an invalid email format', async () => {
    const response = await request(app.getHttpServer()).post('/api/auth/login').send({
      email: 'invalid-email',
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        email: ['email must be a valid email address'],
      },
    });
  });

  it('returns forbidden when the account is inactive', async () => {
    const email = uniqueEmail('login.inactive');
    await registerVerifiedUser(email);

    const connection = app.get<Connection>(getConnectionToken());
    await connection.collection('users').updateOne({ email }, { $set: { is_active: false } });

    const response = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(403);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('This account is inactive. Please contact support for assistance.');
    expect(response.body.error).toEqual({
      code: 'USER_INACTIVE',
      details: null,
    });
  });

  it('returns unauthorized for an incorrect password', async () => {
    const email = uniqueEmail('login.bad-password');
    await registerVerifiedUser(email);

    const response = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password: 'WrongPassword123!',
    });

    expect(response.status).toBe(401);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Email or password is incorrect');
    expect(response.body.error).toEqual({
      code: 'INVALID_CREDENTIALS',
      details: null,
    });
  });

  it('returns validation error for a weak password', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/auth/login')
      .send({
        email: uniqueEmail('login.weak-password'),
        password: 'weak',
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        password: [
          'password must be at least 8 characters and include an uppercase letter, lowercase letter, and number',
        ],
      },
    });
  });

  it('returns forbidden when email is not verified', async () => {
    const email = uniqueEmail('login.unverified');

    await request(app.getHttpServer())
      .post('/api/auth/signup')
      .send({
        first_name: 'Jane',
        last_name: 'Doe',
        email,
        password: 'StrongPassword123!',
        terms_accepted: true,
      })
      .expect(201);

    const response = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(403);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Please verify your email address before signing in.');
    expect(response.body.error).toEqual({
      code: 'EMAIL_NOT_VERIFIED',
      details: null,
    });
  });

  it('refreshes tokens with a valid refresh token', async () => {
    const email = uniqueEmail('session.refresh');
    await registerVerifiedUser(email);

    const loginResponse = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password: 'StrongPassword123!',
    });

    const refreshToken = loginResponse.body.data.refreshToken as string;

    const response = await request(app.getHttpServer()).post('/api/auth/refresh').send({ refreshToken });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Tokens refreshed successfully');
    expect(response.body.data).toEqual({
      accessToken: expect.any(String),
      refreshToken: expect.any(String),
      tokenType: 'Bearer',
    });
  });

  it('returns validation error for a malformed refresh token', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/auth/refresh')
      .send({ refreshToken: 'not-a-valid-token' });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        refreshToken: ['refreshToken must be a valid JWT'],
      },
    });
  });

  it('returns unauthorized for an invalid refresh token', async () => {
    const response = await request(app.getHttpServer()).post('/api/auth/refresh').send({
      refreshToken:
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRva2VuVXNlIjoicmVmcmVzaCIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjo5OTk5OTk5OTk5fQ.invalid-signature',
    });

    expect(response.status).toBe(401);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Refresh token is invalid or expired');
    expect(response.body.error).toEqual({
      code: 'INVALID_REFRESH_TOKEN',
      details: null,
    });
  });
});

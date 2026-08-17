import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Auth Verify Email (e2e)', () => {
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

  async function signupUser(email: string): Promise<void> {
    await request(app.getHttpServer())
      .post('/api/auth/signup')
      .send({
        first_name: 'John',
        last_name: 'Doe',
        email,
        password: 'StrongPassword123!',
        terms_accepted: true,
      })
      .expect(201);
  }

  it('verifies a registered email address with a valid token', async () => {
    const email = uniqueEmail('verify.success');
    await signupUser(email);

    const token = verificationTokens.get(email);
    expect(token).toBeDefined();

    const response = await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token });

    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      success: true,
      message: 'Email address verified successfully',
      data: {
        id: expect.any(String),
        name: 'John Doe',
        first_name: 'John',
        last_name: 'Doe',
        email,
        email_verified: true,
      },
    });
  });

  it('returns validation error when the token query parameter is missing', async () => {
    const response = await request(app.getHttpServer()).get('/api/auth/verify-email');

    expect(response.status).toBe(422);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Validation failed');
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.token).toEqual(
      expect.arrayContaining(['token is required']),
    );
  });

  it('returns validation error for a malformed token', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/auth/verify-email')
      .query({ token: 'not-a-valid-token' });

    expect(response.status).toBe(422);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        token: ['token is invalid'],
      },
    });
  });

  it('returns bad request for an unknown verification token', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/auth/verify-email')
      .query({ token: 'a'.repeat(64) });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('This email verification link is invalid or has expired');
    expect(response.body.error).toEqual({
      code: 'INVALID_VERIFICATION_TOKEN',
      details: null,
    });
  });

  it('returns bad request when reusing an already consumed token', async () => {
    const email = uniqueEmail('verify.reuse');
    await signupUser(email);

    const token = verificationTokens.get(email);
    expect(token).toBeDefined();

    await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token }).expect(200);

    const response = await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('This email verification link is invalid or has expired');
    expect(response.body.error).toEqual({
      code: 'INVALID_VERIFICATION_TOKEN',
      details: null,
    });
  });

  it('returns bad request for an expired verification token', async () => {
    const email = uniqueEmail('verify.expired');
    await signupUser(email);

    const token = verificationTokens.get(email);
    expect(token).toBeDefined();

    const connection = app.get<Connection>(getConnectionToken());
    await connection.collection('users').updateOne(
      { email },
      { $set: { verification_token_expires_at: new Date(Date.now() - 60_000) } },
    );

    const response = await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('This email verification link is invalid or has expired');
    expect(response.body.error).toEqual({
      code: 'INVALID_VERIFICATION_TOKEN',
      details: null,
    });
  });
});

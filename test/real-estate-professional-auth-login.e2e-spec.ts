import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

const LOGIN_PATH = '/api/v1/real-estate-professional/auth/login';

describe('Real Estate Professional Auth Login (e2e)', () => {
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
      .post('/api/v1/auth/signup')
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
    await request(app.getHttpServer()).get('/api/v1/auth/verify-email').query({ token }).expect(200);
  }

  it('returns 201 and a JWT for valid credentials', async () => {
    const email = uniqueEmail('rep.login.success');
    await registerVerifiedUser(email);

    const response = await request(app.getHttpServer()).post(LOGIN_PATH).send({
      email,
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data.token).toEqual(expect.any(String));
    expect(response.body.data.id).toEqual(expect.any(String));
    expect(response.body.data.email).toBe(email);
  });

  it('returns validation error when email is empty', async () => {
    const response = await request(app.getHttpServer()).post(LOGIN_PATH).send({
      email: '',
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.email).toEqual(expect.arrayContaining([expect.stringContaining('email')]));
  });

  it('returns validation error when password is empty', async () => {
    const response = await request(app.getHttpServer()).post(LOGIN_PATH).send({
      email: uniqueEmail('rep.login.empty-password'),
      password: '',
    });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.password).toEqual(expect.arrayContaining([expect.stringContaining('password')]));
  });

  it('returns 404 when the email is not registered', async () => {
    const response = await request(app.getHttpServer()).post(LOGIN_PATH).send({
      email: uniqueEmail('rep.login.missing-user'),
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(404);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('USER_NOT_FOUND');
  });

  it('returns 401 when the password is incorrect', async () => {
    const email = uniqueEmail('rep.login.bad-password');
    await registerVerifiedUser(email);

    const response = await request(app.getHttpServer()).post(LOGIN_PATH).send({
      email,
      password: 'WrongPassword123!',
    });

    expect(response.status).toBe(401);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('INVALID_CREDENTIALS');
  });

  it('returns 403 when the account is inactive', async () => {
    const email = uniqueEmail('rep.login.inactive');
    await registerVerifiedUser(email);

    const connection = app.get<Connection>(getConnectionToken());
    await connection.collection('users').updateOne({ email }, { $set: { is_active: false } });

    const response = await request(app.getHttpServer()).post(LOGIN_PATH).send({
      email,
      password: 'StrongPassword123!',
    });

    expect(response.status).toBe(403);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('USER_INACTIVE');
  });
});
import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

const LOGIN_PATH = '/api/v1/real-estate-professional/auth/login';
const LOGOUT_PATH = '/api/v1/real-estate-professional/auth/logout';

describe('Real Estate Professional Auth Logout (e2e)', () => {
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

  it('logs out successfully with a valid access token', async () => {
    const email = uniqueEmail('rep.logout.success');
    await registerVerifiedUser(email);

    const loginResponse = await request(app.getHttpServer()).post(LOGIN_PATH).send({
      email,
      password: 'StrongPassword123!',
    });
    const accessToken = loginResponse.body.data.accessToken as string;

    const response = await request(app.getHttpServer())
      .get(LOGOUT_PATH)
      .set('Authorization', `Bearer ${accessToken}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Signed out successfully');

    const guarded = await request(app.getHttpServer())
      .get('/api/v1/profile')
      .set('Authorization', `Bearer ${accessToken}`);

    expect(guarded.status).toBe(401);
    expect(guarded.body.error.code).toBe('INVALID_TOKEN');
  });

  it('returns unauthorized when no bearer token is supplied', async () => {
    const response = await request(app.getHttpServer()).get(LOGOUT_PATH);

    expect(response.status).toBe(401);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
  });
});
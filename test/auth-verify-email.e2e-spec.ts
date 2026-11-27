import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { getConnection } from 'typeorm';

describe('Auth Verify Email E2E', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await getConnection().close();
    await app.close();
  });

  it('should verify email successfully with valid token', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/v1/auth/verify-email?token=validtoken')
      .expect(200);
    expect(response.body).toEqual({ message: 'Email verified successfully' });
  });

  it('should return 400 for invalid token', async () => {
    await request(app.getHttpServer())
      .get('/api/v1/auth/verify-email?token=invalidtoken')
      .expect(400);
  });

  it('should return 404 for missing token', async () => {
    await request(app.getHttpServer())
      .get('/api/v1/auth/verify-email')
      .expect(404);
  });
});
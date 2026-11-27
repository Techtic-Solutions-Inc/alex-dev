import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { getConnection } from 'typeorm';

describe('Auth Login E2E', () => {
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

  it('should login successfully with valid credentials', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/auth/login')
      .send({ email: 'user@test.com', password: 'TestUser123!' })
      .expect(200);
    expect(response.body).toHaveProperty('accessToken');
  });

  it('should return 401 for invalid credentials', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/auth/login')
      .send({ email: 'user@test.com', password: 'wrongpassword' })
      .expect(401);
  });

  it('should return 400 for missing email', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/auth/login')
      .send({ password: 'TestUser123!' })
      .expect(400);
  });

  it('should return 400 for missing password', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/auth/login')
      .send({ email: 'user@test.com' })
      .expect(400);
  });
});
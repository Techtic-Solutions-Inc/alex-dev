import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { getConnection } from 'typeorm';

describe('Auth Signup E2E', () => {
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

  it('should signup successfully with valid data', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/auth/signup')
      .send({ email: 'newuser@test.com', password: 'NewUser123!' })
      .expect(201);
    expect(response.body).toHaveProperty('id');
  });

  it('should return 409 for duplicate email', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/auth/signup')
      .send({ email: 'user@test.com', password: 'TestUser123!' })
      .expect(409);
  });

  it('should return 400 for missing email', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/auth/signup')
      .send({ password: 'NewUser123!' })
      .expect(400);
  });

  it('should return 400 for missing password', async () => {
    await request(app.getHttpServer())
      .post('/api/v1/auth/signup')
      .send({ email: 'newuser@test.com' })
      .expect(400);
  });
});
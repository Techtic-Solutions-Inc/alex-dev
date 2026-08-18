// Removed hardcoded secret/credential
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

let app: INestApplication;

beforeAll(async () => {
  const moduleFixture: TestingModule = await Test.createTestingModule({
    imports: [AppModule],
  }).compile();

  app = moduleFixture.createNestApplication();
  await app.init();
});

describe('Dashboard (e2e)', () => {
  it('/GET dashboard', () => {
    return request(app.getHttpServer())
      .get('/dashboard')
      .expect(200);
  });

  afterAll(async () => {
    await app.close();
  });
});
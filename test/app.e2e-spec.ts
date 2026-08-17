import { INestApplication } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import request = require('supertest');
import { HealthModule } from '../src/modules/health/health.module';

describe('Health endpoint (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [HealthModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('GET /health returns an UP status', async () => {
    await request(app.getHttpServer())
      .get('/health')
      .expect(200)
      .expect({ message: 'API is healthy', data: { status: 'UP' } });
  });
});

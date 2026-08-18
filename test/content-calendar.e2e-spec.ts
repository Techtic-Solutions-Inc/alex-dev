// Restored e2e tests from commit 042a063
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Content Calendar (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/api/content-calendar (GET)', () => {
    return request(app.getHttpServer())
      .get('/api/content-calendar')
      .set('Authorization', 'Bearer valid-token')
      .expect(200)
      .expect({ /* expected response */ });
  });

  afterAll(async () => {
    await app.close();
  });
});
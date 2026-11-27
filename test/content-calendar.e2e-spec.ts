import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { getConnection } from 'typeorm';

describe('Content Calendar E2E', () => {
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

  it('should return calendar events', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/v1/calendar/events')
      .expect(200);
    expect(Array.isArray(response.body)).toBe(true);
  });

  it('should return 404 for non-existent calendar', async () => {
    await request(app.getHttpServer())
      .get('/api/v1/calendar/non-existent')
      .expect(404);
  });
});
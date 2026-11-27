import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { clearUsers, createTestApp } from './create-test-app';

describe('Structured logging (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createTestApp();
  });

  afterAll(async () => {
    await clearUsers(app);
    await app.close();
  });

  it('returns a correlation id header for every request', async () => {
    const response = await request(app.getHttpServer()).get('/api/v1/health').expect(200);

    const requestId = response.headers['x-request-id'];
    expect(requestId).toEqual(expect.any(String));
    expect(String(requestId).length).toBeGreaterThan(8);
  });

  it('echoes a provided X-Request-Id header', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/v1/health')
      .set('X-Request-Id', 'client-trace-001')
      .expect(200);

    expect(response.headers['x-request-id']).toBe('client-trace-001');
  });
});
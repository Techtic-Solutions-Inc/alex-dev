import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { createTestApp } from './create-test-app';

describe('Health endpoint (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createTestApp();
  });

  afterAll(async () => {
    await app.close();
  });

  it('GET /health returns an UP status and frontend session bootstrap fields', async () => {
    const response = await request(app.getHttpServer()).get('/health').expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('API is healthy');
    expect(response.body.data).toEqual({
      status: 'UP',
      id: null,
      name: null,
      first_name: null,
      last_name: null,
      email: null,
      token: null,
    });
  });
});

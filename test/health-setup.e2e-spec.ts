import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { createTestApp } from './create-test-app';

describe('Setup: GET /api/v1/health (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createTestApp();
  });

  afterAll(async () => {
    await app.close();
  });

  it('returns validation error envelope for invalid bearer-only prefix', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/v1/auth/signup')
      .send({
        first_name: '',
        last_name: 'User',
        email: 'not-an-email',
        password: 'short',
        terms_accepted: false,
      })
      .expect(400);

    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Validation failed');
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        first_name: expect.any(Array),
        email: expect.any(Array),
        password: expect.any(Array),
        terms_accepted: expect.any(Array),
      }),
    );
  });

  it('returns 200 with success envelope and UP status when database is connected', async () => {
    const response = await request(app.getHttpServer()).get('/api/v1/health').expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('API is healthy');
    expect(response.body.data).toEqual(
      expect.objectContaining({
        status: 'UP',
        id: null,
        name: null,
        full_name: null,
        first_name: null,
        last_name: null,
        email: null,
        phone: null,
        token: null,
        bio: null,
        city: null,
        country: null,
        zip: null,
        address: null,
        image: null,
        password: null,
        profile: null,
        system_health: expect.objectContaining({
          uptime_seconds: expect.any(Number),
          memory_heap_used_mb: expect.any(Number),
          memory_rss_mb: expect.any(Number),
          event_loop_delay_ms: expect.any(Number),
          apm_enabled: expect.any(Boolean),
        }),
      }),
    );
  });
});

import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { clearUsers, createTestApp } from './create-test-app';

describe('Security headers (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createTestApp();
  });

  afterAll(async () => {
    await clearUsers(app);
    await app.close();
  });

  it('returns hardened headers on the health endpoint', async () => {
    const response = await request(app.getHttpServer()).get('/api/v1/health').expect(200);

    expect(response.headers['x-content-type-options']).toBe('nosniff');
    expect(response.headers['x-frame-options']).toBe('DENY');
    expect(response.headers['referrer-policy']).toBe('strict-origin-when-cross-origin');
    expect(response.headers['cross-origin-resource-policy']).toBe('same-site');
    expect(response.headers['x-powered-by']).toBeUndefined();
  });

  it('redirects to HTTPS when FORCE_HTTPS is enabled and X-Forwarded-Proto is http', async () => {
    const previous = process.env.FORCE_HTTPS;
    process.env.FORCE_HTTPS = 'true';

    const redirectApp = await createTestApp();

    try {
      const response = await request(redirectApp.getHttpServer())
        .get('/api/v1/health')
        .set('X-Forwarded-Proto', 'http')
        .set('Host', 'api.example.com');

      expect(response.status).toBe(301);
      expect(response.headers.location).toBe('https://api.example.com/api/v1/health');
    } finally {
      await clearUsers(redirectApp);
      await redirectApp.close();
      if (previous === undefined) {
        delete process.env.FORCE_HTTPS;
      } else {
        process.env.FORCE_HTTPS = previous;
      }
    }
  });
});
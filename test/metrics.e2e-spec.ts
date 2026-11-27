import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { clearUsers, createTestApp } from './create-test-app';

describe('Prometheus metrics (e2e)', () => {
  let app: INestApplication;
  const previousMetricsEnabled = process.env.METRICS_ENABLED;

  beforeAll(async () => {
    process.env.METRICS_ENABLED = 'true';
    app = await createTestApp();
  });

  afterAll(async () => {
    await clearUsers(app);
    await app.close();
    if (previousMetricsEnabled === undefined) {
      delete process.env.METRICS_ENABLED;
    } else {
      process.env.METRICS_ENABLED = previousMetricsEnabled;
    }
  });

  it('exposes Prometheus metrics after requests are recorded', async () => {
    await request(app.getHttpServer()).get('/api/v1/health').expect(200);

    const response = await request(app.getHttpServer()).get('/metrics').expect(200);

    expect(response.headers['content-type']).toContain('text/plain');
    expect(response.text).toContain('# TYPE backend_api_http_requests_total counter');
    expect(response.text).toContain('backend_api_event_loop_delay_ms');
  });
});

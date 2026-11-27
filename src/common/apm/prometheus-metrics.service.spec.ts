import { PrometheusMetricsService } from './prometheus-metrics.service';

describe('PrometheusMetricsService', () => {
  const originalMetricsEnabled = process.env.METRICS_ENABLED;

  beforeEach(() => {
    process.env.METRICS_ENABLED = 'true';
    process.env.METRICS_PREFIX = 'backend_api';
  });

  afterEach(() => {
    if (originalMetricsEnabled === undefined) {
      delete process.env.METRICS_ENABLED;
    } else {
      process.env.METRICS_ENABLED = originalMetricsEnabled;
    }
  });

  it('renders Prometheus text after recording HTTP metrics', () => {
    const metrics = new PrometheusMetricsService();

    metrics.recordHttpRequest({
      method: 'GET',
      route: '/api/v1/health',
      statusCode: 200,
      durationMs: 42.5,
      slow: false,
    });
    metrics.updateRuntimeGauges({
      uptimeSeconds: 120,
      heapUsedBytes: 50_000_000,
      rssBytes: 75_000_000,
      eventLoopDelayMs: 2.1,
    });

    const rendered = metrics.renderMetrics();

    expect(rendered).toContain('# TYPE backend_api_http_requests_total counter');
    expect(rendered).toContain('backend_api_http_requests_total{method="GET"');
    expect(rendered).toContain('# TYPE backend_api_http_request_duration_ms histogram');
    expect(rendered).toContain('backend_api_process_uptime_seconds');
    expect(rendered).toContain('backend_api_event_loop_delay_ms');
  });
});
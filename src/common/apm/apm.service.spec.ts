import { ConfigModule } from '@nestjs/config';
import { Test, TestingModule } from '@nestjs/testing';
import { ApmService } from './apm.service';
import { EventLoopMonitorService } from './event-loop-monitor.service';

describe('ApmService', () => {
  let service: ApmService;

  beforeEach(async () => {
    process.env.APM_ENABLED = 'false';

    const module: TestingModule = await Test.createTestingModule({
      imports: [ConfigModule.forRoot({ isGlobal: true })],
      providers: [EventLoopMonitorService, ApmService],
    }).compile();

    await module.init();
    service = module.get(ApmService);
  });

  it('records HTTP metrics without throwing when APM is disabled', () => {
    expect(() =>
      service.recordHttpRequest({
        method: 'GET',
        route: '/api/v1/health',
        statusCode: 200,
        durationMs: 12,
      }),
    ).not.toThrow();
    expect(service.isEnabled()).toBe(false);
  });

  it('exposes runtime health snapshot fields', () => {
    const snapshot = service.getSystemHealthSnapshot();
    expect(snapshot).toEqual(
      expect.objectContaining({
        uptime_seconds: expect.any(Number),
        memory_heap_used_mb: expect.any(Number),
        memory_rss_mb: expect.any(Number),
        event_loop_delay_ms: expect.any(Number),
        apm_enabled: false,
        apm_provider: null,
      }),
    );
  });

  it('flags slow requests via logging path without external exporter', () => {
    process.env.APM_SLOW_REQUEST_THRESHOLD_MS = '5';
    const monitor = new EventLoopMonitorService();
    const slowService = new ApmService(monitor);
    expect(() =>
      slowService.recordHttpRequest({
        method: 'GET',
        route: '/api/v1/content',
        statusCode: 200,
        durationMs: 50,
      }),
    ).not.toThrow();
  });
});

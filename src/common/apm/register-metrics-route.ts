import { INestApplication } from '@nestjs/common';
import { Request, Response } from 'express';
import { ApmService } from './apm.service';
import { PrometheusMetricsService } from './prometheus-metrics.service';

export const registerPrometheusMetricsRoute = (app: INestApplication): void => {
  const prometheusMetrics = app.get(PrometheusMetricsService);
  if (!prometheusMetrics.isEnabled()) {
    return;
  }

  const apmService = app.get(ApmService);
  const expressInstance = app.getHttpAdapter().getInstance();

  expressInstance.get('/metrics', (_request: Request, response: Response) => {
    const snapshot = apmService.getSystemHealthSnapshot();
    const memory = process.memoryUsage();
    prometheusMetrics.updateRuntimeGauges({
      uptimeSeconds: snapshot.uptime_seconds,
      heapUsedBytes: memory.heapUsed,
      rssBytes: memory.rss,
      eventLoopDelayMs: snapshot.event_loop_delay_ms,
    });
    response.status(200).type('text/plain; version=0.0.4; charset=utf-8').send(prometheusMetrics.renderMetrics());
  });
};

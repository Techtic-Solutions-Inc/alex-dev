import { Injectable } from '@nestjs/common';
import logger from '../services/logger.service';
import { readApmConfig } from './apm.config';
import { ApmConfig, HttpRequestMetric, SystemHealthSnapshot } from './apm.types';
import { EventLoopMonitorService } from './event-loop-monitor.service';

type StatsClient = {
  increment: (name: string, value?: number, tags?: Record<string, string>) => void;
  histogram: (name: string, value: number, tags?: Record<string, string>) => void;
};

@Injectable()
export class ApmService {
  private readonly config: ApmConfig;
  private readonly statsClient: StatsClient | null;

  constructor(private readonly eventLoopMonitor: EventLoopMonitorService) {
    this.config = readApmConfig();
    this.statsClient = this.resolveStatsClient();
  }

  isEnabled(): boolean {
    return this.config.enabled;
  }

  getConfig(): ApmConfig {
    return this.config;
  }

  recordHttpRequest(metric: HttpRequestMetric): void {
    const tags = {
      method: metric.method,
      route: metric.route,
      status: String(metric.statusCode),
      error: metric.error ? 'true' : 'false',
    };

    this.statsClient?.increment('api.http.requests', 1, tags);
    this.statsClient?.histogram('api.http.request.duration_ms', metric.durationMs, tags);

    if (metric.durationMs >= this.config.slowRequestThresholdMs) {
      logger.warn('Slow HTTP request detected', {
        method: metric.method,
        route: metric.route,
        statusCode: metric.statusCode,
        durationMs: metric.durationMs,
        thresholdMs: this.config.slowRequestThresholdMs,
      });
      this.statsClient?.increment('api.http.slow_requests', 1, tags);
    }
  }

  recordError(name: string, message: string): void {
    this.statsClient?.increment('api.errors', 1, { name, message: message.slice(0, 120) });
  }

  getSystemHealthSnapshot(): SystemHealthSnapshot {
    const memory = process.memoryUsage();
    return {
      uptime_seconds: Math.floor(process.uptime()),
      memory_heap_used_mb: Number((memory.heapUsed / (1024 * 1024)).toFixed(2)),
      memory_rss_mb: Number((memory.rss / (1024 * 1024)).toFixed(2)),
      event_loop_delay_ms: this.eventLoopMonitor.getMeanDelayMs(),
      apm_enabled: this.config.enabled,
      apm_provider: this.config.enabled ? this.config.provider : null,
    };
  }

  private resolveStatsClient(): StatsClient | null {
    if (!this.config.enabled) {
      return null;
    }

    if (this.config.provider === 'datadog') {
      try {
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        const tracer = require('dd-trace') as { dogstatsd?: StatsClient };
        return tracer.dogstatsd ?? null;
      } catch {
        return null;
      }
    }

    return {
      increment: (name, value = 1, tags) => {
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        const newrelic = require('newrelic') as {
          recordMetric: (metric: string, value: number) => void;
        };
        const suffix = tags ? `:${Object.entries(tags).map(([k, v]) => `${k}=${v}`).join(',')}` : '';
        newrelic.recordMetric(`${name}${suffix}`, value);
      },
      histogram: (name, value, tags) => {
        // eslint-disable-next-line @typescript-eslint/no-require-imports
        const newrelic = require('newrelic') as {
          recordMetric: (metric: string, value: number) => void;
        };
        const suffix = tags ? `:${Object.entries(tags).map(([k, v]) => `${k}=${v}`).join(',')}` : '';
        newrelic.recordMetric(`${name}${suffix}`, value);
      },
    };
  }
}
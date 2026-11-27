export type ApmProvider = 'datadog' | 'newrelic';

export interface ApmConfig {
  readonly enabled: boolean;
  readonly provider: ApmProvider;
  readonly serviceName: string;
  readonly environment: string;
  readonly version: string;
  readonly slowRequestThresholdMs: number;
}

export interface HttpRequestMetric {
  readonly method: string;
  readonly route: string;
  readonly statusCode: number;
  readonly durationMs: number;
  readonly error?: boolean;
}

export interface SystemHealthSnapshot {
  readonly uptime_seconds: number;
  readonly memory_heap_used_mb: number;
  readonly memory_rss_mb: number;
  readonly event_loop_delay_ms: number;
  readonly apm_enabled: boolean;
  readonly apm_provider: string | null;
}

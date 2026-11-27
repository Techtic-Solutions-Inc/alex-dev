export interface LoggingAggregationConfig {
  readonly serviceName: string;
  readonly environment: string;
  readonly version: string;
  readonly logstashHttpUrl: string | null;
  readonly logstashEnabled: boolean;
  readonly logstashBatchSize: number;
  readonly logstashFlushIntervalMs: number;
}

const truthy = (value: string | undefined): boolean => {
  if (!value) {
    return false;
  }
  const normalized = value.trim().toLowerCase();
  return normalized === '1' || normalized === 'true' || normalized === 'yes' || normalized === 'on';
};

const parsePositiveInt = (value: string | undefined, fallback: number): number => {
  if (!value || !/^\d+$/.test(value.trim())) {
    return fallback;
  }
  const parsed = Number(value);
  return Number.isSafeInteger(parsed) && parsed > 0 ? parsed : fallback;
};

export const readLoggingAggregationConfig = (
  environment: Record<string, string | undefined> = process.env,
): LoggingAggregationConfig => {
  const logstashHttpUrl = environment.LOGSTASH_HTTP_URL?.trim() || environment.ELASTICSEARCH_LOGS_URL?.trim() || null;

  return {
    serviceName: environment.LOG_SERVICE_NAME?.trim() || environment.DD_SERVICE?.trim() || 'backend-api',
    environment: environment.DD_ENV?.trim() || environment.NODE_ENV?.trim() || 'development',
    version: environment.DD_VERSION?.trim() || environment.npm_package_version?.trim() || '1.0.0',
    logstashHttpUrl,
    logstashEnabled: truthy(environment.LOGSTASH_ENABLED) || Boolean(logstashHttpUrl),
    logstashBatchSize: parsePositiveInt(environment.LOGSTASH_BATCH_SIZE, 25),
    logstashFlushIntervalMs: parsePositiveInt(environment.LOGSTASH_FLUSH_INTERVAL_MS, 2000),
  };
};

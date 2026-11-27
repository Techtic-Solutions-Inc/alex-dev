export interface PrometheusMetricsConfig {
  readonly enabled: boolean;
  readonly prefix: string;
  readonly defaultHistogramBucketsMs: readonly number[];
}

const truthy = (value: string | undefined): boolean => {
  if (!value) {
    return false;
  }
  const normalized = value.trim().toLowerCase();
  return normalized === '1' || normalized === 'true' || normalized === 'yes' || normalized === 'on';
};

export const readPrometheusMetricsConfig = (
  environment: Record<string, string | undefined> = process.env,
): PrometheusMetricsConfig => {
  const nodeEnv = environment.NODE_ENV?.trim() ?? 'development';
  const enabledByDefault = nodeEnv === 'production' || nodeEnv === 'staging';

  const rawPrefix = environment.METRICS_PREFIX?.trim() || 'backend_api';
  const prefix = /^[a-z][a-z0-9_]*$/.test(rawPrefix) ? rawPrefix : 'backend_api';

  return {
    enabled: environment.METRICS_ENABLED === undefined ? enabledByDefault : truthy(environment.METRICS_ENABLED),
    prefix,
    defaultHistogramBucketsMs: [25, 50, 100, 250, 500, 1000, 2500, 5000, 10_000],
  };
};

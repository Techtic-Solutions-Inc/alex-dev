import { ApmConfig, ApmProvider } from './apm.types';

const ALLOWED_PROVIDERS: readonly ApmProvider[] = ['datadog', 'newrelic'];

function parseProvider(value: string | undefined): ApmProvider {
  const normalized = value?.trim().toLowerCase();
  if (normalized && (ALLOWED_PROVIDERS as readonly string[]).includes(normalized)) {
    return normalized as ApmProvider;
  }
  return 'datadog';
}

function parsePositiveInt(value: string | undefined, fallback: number): number {
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < 1) {
    return fallback;
  }
  return Math.floor(parsed);
}

export function readApmConfig(environment: Record<string, string | undefined> = process.env): ApmConfig {
  return {
    enabled: environment.APM_ENABLED === 'true',
    provider: parseProvider(environment.APM_PROVIDER),
    serviceName: environment.DD_SERVICE?.trim() || environment.NEW_RELIC_APP_NAME?.trim() || 'backend-api',
    environment: environment.DD_ENV?.trim() || environment.NODE_ENV?.trim() || 'development',
    version: environment.DD_VERSION?.trim() || environment.npm_package_version?.trim() || '1.0.0',
    slowRequestThresholdMs: parsePositiveInt(environment.APM_SLOW_REQUEST_THRESHOLD_MS, 2000),
  };
}

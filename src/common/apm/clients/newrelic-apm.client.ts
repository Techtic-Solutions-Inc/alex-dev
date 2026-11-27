import { ApmConfig } from '../apm.types';

export function initializeNewRelicApm(config: ApmConfig): void {
  if (!process.env.NEW_RELIC_LICENSE_KEY?.trim()) {
    throw new Error('NEW_RELIC_LICENSE_KEY is required when APM_PROVIDER is newrelic.');
  }

  process.env.NEW_RELIC_APP_NAME ??= config.serviceName;
  process.env.NEW_RELIC_DISTRIBUTED_TRACING_ENABLED ??= 'true';
  process.env.NEW_RELIC_LOG_ENABLED ??= 'false';

  // eslint-disable-next-line @typescript-eslint/no-require-imports
  require('newrelic');
}

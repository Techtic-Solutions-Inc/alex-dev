import logger from '../services/logger.service';
import { readApmConfig } from './apm.config';
import { initializeDatadogApm } from './clients/datadog-apm.client';
import { initializeNewRelicApm } from './clients/newrelic-apm.client';

export function bootstrapApm(): void {
  const config = readApmConfig();

  if (!config.enabled) {
    return;
  }

  try {
    if (config.provider === 'newrelic') {
      initializeNewRelicApm(config);
    } else {
      initializeDatadogApm(config);
    }

    logger.info('APM initialized', {
      provider: config.provider,
      service: config.serviceName,
      environment: config.environment,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown APM bootstrap error';
    logger.warn('APM bootstrap failed; continuing without external APM', { message });
  }
}

bootstrapApm();

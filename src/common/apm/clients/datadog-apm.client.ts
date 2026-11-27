import { ApmConfig } from '../apm.types';

export function initializeDatadogApm(config: ApmConfig): void {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const tracer = require('dd-trace') as {
    init: (options: Record<string, unknown>) => unknown;
  };

  tracer.init({
    service: config.serviceName,
    env: config.environment,
    version: config.version,
    logInjection: true,
    runtimeMetrics: true,
    profiling: process.env.DD_PROFILING_ENABLED === 'true',
    appsec: false,
    hostname: process.env.DD_AGENT_HOST,
    port: process.env.DD_TRACE_AGENT_PORT ? Number(process.env.DD_TRACE_AGENT_PORT) : undefined,
  });
}

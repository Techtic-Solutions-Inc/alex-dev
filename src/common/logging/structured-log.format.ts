import { format } from 'winston';
import { LoggingAggregationConfig } from '../../config/logging.config';

const SENSITIVE_KEY_PATTERN =
  /(password|passwd|authorization|token|secret|api[_-]?key|refresh[_-]?token|access[_-]?token)/i;

export const redactSensitiveValues = (value: unknown): unknown => {
  if (Array.isArray(value)) {
    return value.map((entry) => redactSensitiveValues(entry));
  }

  if (typeof value === 'object' && value !== null) {
    return Object.entries(value as Record<string, unknown>).reduce<Record<string, unknown>>((acc, [key, nested]) => {
      if (SENSITIVE_KEY_PATTERN.test(key)) {
        acc[key] = '[REDACTED]';
        return acc;
      }
      acc[key] = redactSensitiveValues(nested);
      return acc;
    }, {});
  }

  return value;
};

export const createStructuredLogFormat = (config: LoggingAggregationConfig) =>
  format((info) => {
    const redacted = redactSensitiveValues({ ...info }) as Record<string, unknown>;
    for (const [key, value] of Object.entries(redacted)) {
      if (key !== 'level' && key !== 'message') {
        Reflect.set(info, key, value);
      }
    }

    const requestId = typeof info.requestId === 'string' ? info.requestId : undefined;
    Object.assign(info, {
      '@version': '1',
      service: {
        name: config.serviceName,
        version: config.version,
      },
      environment: config.environment,
      ...(requestId ? { trace: { request_id: requestId } } : {}),
      ecs: { version: '1.12.0' },
    });

    return info;
  });

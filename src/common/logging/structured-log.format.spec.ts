import { createLogger, format, transports } from 'winston';
import { readLoggingAggregationConfig } from '../../config/logging.config';
import { createStructuredLogFormat, redactSensitiveValues } from './structured-log.format';

describe('structured log format', () => {
  it('redacts sensitive keys recursively', () => {
    const redacted = redactSensitiveValues({
      email: 'user@example.com',
      password: 'Secret123!',
      headers: {
        authorization: 'Bearer token-value',
      },
    });

    expect(redacted).toEqual({
      email: 'user@example.com',
      password: '[REDACTED]',
      headers: {
        authorization: '[REDACTED]',
      },
    });
  });

  it('adds service metadata and trace identifiers', () => {
    let captured: Record<string, unknown> | undefined;
    const structuredFormat = createStructuredLogFormat(
      readLoggingAggregationConfig({
        LOG_SERVICE_NAME: 'backend-api',
        DD_ENV: 'test',
        DD_VERSION: '9.9.9',
      }),
    )();
    const probe = createLogger({
      format: format.combine(
        structuredFormat,
        format((info) => {
          captured = { ...info };
          return info;
        })(),
      ),
      transports: [new transports.Console({ silent: true })],
    });

    probe.info('HTTP request completed', { requestId: 'req-123' });

    expect(captured).toEqual(
      expect.objectContaining({
        message: 'HTTP request completed',
        service: { name: 'backend-api', version: '9.9.9' },
        environment: 'test',
        trace: { request_id: 'req-123' },
        ecs: { version: '1.12.0' },
      }),
    );
  });
});

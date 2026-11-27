import { createLogger, format, transports } from 'winston';
import { LogstashHttpTransport } from '../logging/logstash-http.transport';
import { readLoggingAggregationConfig } from '../../config/logging.config';
import { createLogShippingStream } from '../logging/logstash-http.transport';
import { createStructuredLogFormat } from '../logging/structured-log.format';

export const buildApplicationLogger = () => {
  const aggregationConfig = readLoggingAggregationConfig();
  const structuredFormat = createStructuredLogFormat(aggregationConfig);

  const loggerTransports: Array<transports.ConsoleTransportInstance | LogstashHttpTransport> = [new transports.Console()];
  const logstashTransport = createLogShippingStream(aggregationConfig);
  if (logstashTransport) {
    loggerTransports.push(logstashTransport);
  }

  return createLogger({
    level: process.env.LOG_LEVEL ?? 'info',
    defaultMeta: {
      service: aggregationConfig.serviceName,
      environment: aggregationConfig.environment,
    },
    format: format.combine(
      format.timestamp(),
      format.errors({ stack: process.env.NODE_ENV !== 'production' }),
      structuredFormat(),
      format.json(),
    ),
    transports: loggerTransports,
  });
};

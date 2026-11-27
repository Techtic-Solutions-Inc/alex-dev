import TransportStream = require('winston-transport');
import { LoggingAggregationConfig } from '../../config/logging.config';

interface LogstashHttpTransportOptions extends TransportStream.TransportStreamOptions {
  readonly config: LoggingAggregationConfig;
}

/**
 * Ships structured log lines to a Logstash HTTP input or Elasticsearch bulk-compatible receiver.
 */
export class LogstashHttpTransport extends TransportStream {
  private readonly config: LoggingAggregationConfig;
  private readonly queue: string[] = [];
  private flushTimer: NodeJS.Timeout | null = null;
  private flushing = false;

  constructor(options: LogstashHttpTransportOptions) {
    super(options);
    this.config = options.config;
    this.scheduleFlush();
  }

  override log(info: Record<string, unknown>, callback: () => void): void {
    setImmediate(() => this.emit('logged', info));
    this.queue.push(`${JSON.stringify(info)}\n`);
    if (this.queue.length >= this.config.logstashBatchSize) {
      void this.flushQueue();
    }
    callback();
  }

  override close(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }
    void this.flushQueue();
  }

  private scheduleFlush(): void {
    this.flushTimer = setInterval(() => {
      void this.flushQueue();
    }, this.config.logstashFlushIntervalMs);
    this.flushTimer.unref?.();
  }

  private async flushQueue(): Promise<void> {
    if (this.flushing || this.queue.length === 0 || !this.config.logstashHttpUrl) {
      return;
    }

    this.flushing = true;
    const payload = this.queue.splice(0, this.queue.length).join('');

    try {
      const response = await fetch(this.config.logstashHttpUrl, {
        method: 'POST',
        headers: {
          'content-type': 'application/x-ndjson',
        },
        body: payload,
        signal: AbortSignal.timeout(5_000),
      });

      if (!response.ok) {
        process.stderr.write(
          `Log shipping failed with status ${response.status}; ${this.queue.length} entries retained in memory.\n`,
        );
        this.queue.unshift(...payload.split('\n').filter((line) => line.trim().length > 0));
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      process.stderr.write(`Log shipping could not be completed: ${message}\n`);
      this.queue.unshift(...payload.split('\n').filter((line) => line.trim().length > 0));
    } finally {
      this.flushing = false;
    }
  }
}

export const createLogShippingStream = (config: LoggingAggregationConfig): LogstashHttpTransport | null => {
  if (!config.logstashEnabled || !config.logstashHttpUrl) {
    return null;
  }
  return new LogstashHttpTransport({ config });
};

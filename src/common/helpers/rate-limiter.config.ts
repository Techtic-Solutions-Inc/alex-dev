import { ConfigService } from '@nestjs/config';

/**
 * Supported rate-limiting algorithms.
 *
 * - `fixed`: Resets the counter on a fixed time boundary (via `rate-limiter-flexible` in-memory store).
 * - `sliding`: Counts only requests that fall inside the last `RATE_LIMIT_DURATION` seconds.
 */
export type RateLimitStrategy = 'fixed' | 'sliding';

export interface RateLimiterOptions {
  points: number;
  durationSeconds: number;
  strategy: RateLimitStrategy;
}

const DEFAULT_POINTS = 5;
const DEFAULT_DURATION_SECONDS = 1;

/**
 * Reads rate limiter settings from the environment / {@link ConfigService}.
 *
 * | Variable | Description | Default |
 * | --- | --- | --- |
 * | `RATE_LIMIT_POINTS` | Max requests per window per client | `5` (prod); see `env.defaults` in non-prod) |
 * | `RATE_LIMIT_DURATION` | Window length in seconds | `1` |
 * | `RATE_LIMIT_STRATEGY` | `fixed` or `sliding` | `fixed` |
 */
export function parseRateLimiterConfig(configService: ConfigService): RateLimiterOptions {
  const points = Number(configService.get<string>('RATE_LIMIT_POINTS', String(DEFAULT_POINTS)));
  const durationSeconds = Number(configService.get<string>('RATE_LIMIT_DURATION', String(DEFAULT_DURATION_SECONDS)));
  const strategyRaw = (configService.get<string>('RATE_LIMIT_STRATEGY', 'fixed') ?? 'fixed').toLowerCase();

  return {
    points: Number.isInteger(points) && points > 0 ? points : DEFAULT_POINTS,
    durationSeconds: Number.isInteger(durationSeconds) && durationSeconds > 0 ? durationSeconds : DEFAULT_DURATION_SECONDS,
    strategy: strategyRaw === 'sliding' ? 'sliding' : 'fixed',
  };
}
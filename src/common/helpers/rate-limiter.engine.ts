import { RateLimiterMemory, RateLimiterRes } from 'rate-limiter-flexible';
import { RateLimiterOptions } from './rate-limiter.config';

export class RateLimitExceededError extends Error {
  readonly msBeforeNext: number;

  constructor(msBeforeNext: number) {
    super('RATE_LIMITED');
    this.name = 'RateLimitExceededError';
    this.msBeforeNext = msBeforeNext;
  }
}

export interface RateLimitEngine {
  consume(key: string): Promise<void>;
}

/**
 * Fixed-window limiter backed by `rate-limiter-flexible` (one counter per key per duration).
 */
export class FixedWindowRateLimitEngine implements RateLimitEngine {
  private readonly limiter: RateLimiterMemory;

  constructor(options: RateLimiterOptions) {
    this.limiter = new RateLimiterMemory({
      points: options.points,
      duration: options.durationSeconds,
    });
  }

  async consume(key: string): Promise<void> {
    try {
      await this.limiter.consume(key);
    } catch (rejected: unknown) {
      if (rejected instanceof RateLimiterRes) {
        throw new RateLimitExceededError(rejected.msBeforeNext);
      }
      throw rejected;
    }
  }
}

/**
 * In-memory sliding-window limiter: only timestamps within the last `durationSeconds` count toward the limit.
 */
export class SlidingWindowRateLimitEngine implements RateLimitEngine {
  private readonly timestampsByKey = new Map<string, number[]>();

  constructor(private readonly options: RateLimiterOptions) {}

  async consume(key: string): Promise<void> {
    const now = Date.now();
    const windowMs = this.options.durationSeconds * 1000;
    const existing = this.timestampsByKey.get(key) ?? [];
    const active = existing.filter((timestamp) => now - timestamp < windowMs);

    if (active.length >= this.options.points) {
      const oldestInWindow = active[0] ?? now;
      const msBeforeNext = Math.max(0, windowMs - (now - oldestInWindow));
      throw new RateLimitExceededError(msBeforeNext);
    }

    active.push(now);
    this.timestampsByKey.set(key, active);
  }
}

export function createRateLimitEngine(options: RateLimiterOptions): RateLimitEngine {
  return options.strategy === 'sliding'
    ? new SlidingWindowRateLimitEngine(options)
    : new FixedWindowRateLimitEngine(options);
}

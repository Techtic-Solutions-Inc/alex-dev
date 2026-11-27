import { FixedWindowRateLimitEngine, SlidingWindowRateLimitEngine } from './rate-limiter.engine';
import { RateLimitExceededError } from './rate-limiter.engine';

describe('Rate limit engines', () => {
  const options = { points: 2, durationSeconds: 60, strategy: 'fixed' as const };

  describe('FixedWindowRateLimitEngine', () => {
    it('test_rate_limiting_success — allows requests under the limit', async () => {
      const engine = new FixedWindowRateLimitEngine(options);
      await expect(engine.consume('client-a')).resolves.toBeUndefined();
      await expect(engine.consume('client-a')).resolves.toBeUndefined();
    });

    it('test_rate_limiting_exceeded — rejects when the fixed window is full', async () => {
      const engine = new FixedWindowRateLimitEngine(options);
      await engine.consume('client-b');
      await engine.consume('client-b');
      await expect(engine.consume('client-b')).rejects.toBeInstanceOf(RateLimitExceededError);
    });

    it('isolates counters per key', async () => {
      const engine = new FixedWindowRateLimitEngine(options);
      await engine.consume('client-c');
      await engine.consume('client-c');
      await expect(engine.consume('client-d')).resolves.toBeUndefined();
    });
  });

  describe('SlidingWindowRateLimitEngine', () => {
    it('enforces the sliding window limit', async () => {
      const engine = new SlidingWindowRateLimitEngine({ ...options, strategy: 'sliding' });
      await engine.consume('slide-a');
      await engine.consume('slide-a');
      await expect(engine.consume('slide-a')).rejects.toBeInstanceOf(RateLimitExceededError);
    });
  });
});
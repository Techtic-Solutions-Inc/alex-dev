import { HttpStatus, Injectable, NestMiddleware } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { NextFunction, Request, Response } from 'express';
import { parseRateLimiterConfig } from '../common/helpers/rate-limiter.config';
import {
  createRateLimitEngine,
  RateLimitEngine,
  RateLimitExceededError,
} from '../common/helpers/rate-limiter.engine';
import { resolveRateLimitKey } from '../common/helpers/rate-limiter.key';

/**
 * Global HTTP rate limiting middleware.
 *
 * ## Integration
 * Registered in `AppModule.configure()` alongside `LoggerMiddleware` for all routes.
 * Requires `ConfigModule` (global) and `JwtModule` so per-user buckets can be derived from Bearer tokens.
 *
 * ## Configuration (environment)
 * - `RATE_LIMIT_POINTS` — max requests per window (default `5`)
 * - `RATE_LIMIT_DURATION` — window size in seconds (default `1`)
 * - `RATE_LIMIT_STRATEGY` — `fixed` (default) or `sliding`
 *
 * ## Behaviour
 * - Authenticated requests are limited per user id (`sub`); others are limited per IP.
 * - When the limit is exceeded the API responds with HTTP 429 and error code `RATE_LIMITED`.
 */
@Injectable()
export class RateLimiterMiddleware implements NestMiddleware {
  private readonly engine: RateLimitEngine;

  constructor(
    configService: ConfigService,
    private readonly jwtService: JwtService,
  ) {
    this.engine = createRateLimitEngine(parseRateLimiterConfig(configService));
  }

  async use(request: Request, response: Response, next: NextFunction): Promise<void> {
    const key = resolveRateLimitKey(request, this.jwtService);

    try {
      await this.engine.consume(key);
      next();
    } catch (error: unknown) {
      const msBeforeNext = error instanceof RateLimitExceededError ? error.msBeforeNext : 0;
      if (msBeforeNext > 0) {
        response.setHeader('Retry-After', String(Math.ceil(msBeforeNext / 1000)));
      }

      response.status(HttpStatus.TOO_MANY_REQUESTS).json({
        success: false,
        message: 'Too many requests. Please try again shortly.',
        error: { code: 'RATE_LIMITED', details: null },
        path: request.originalUrl ?? request.url,
        timestamp: new Date().toISOString(),
      });
    }
  }
}
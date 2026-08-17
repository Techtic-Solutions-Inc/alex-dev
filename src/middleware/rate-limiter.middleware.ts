import { HttpStatus, Injectable, NestMiddleware } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NextFunction, Request, Response } from 'express';
import { RateLimiterMemory } from 'rate-limiter-flexible';

@Injectable()
export class RateLimiterMiddleware implements NestMiddleware {
  private readonly limiter: RateLimiterMemory;

  constructor(configService: ConfigService) {
    const points = Number(configService.get<string>('RATE_LIMIT_POINTS', '5'));
    const duration = Number(configService.get<string>('RATE_LIMIT_DURATION', '1'));
    this.limiter = new RateLimiterMemory({
      points: Number.isInteger(points) && points > 0 ? points : 5,
      duration: Number.isInteger(duration) && duration > 0 ? duration : 1,
    });
  }

  async use(request: Request, response: Response, next: NextFunction): Promise<void> {
    try {
      await this.limiter.consume(request.ip ?? request.socket.remoteAddress ?? 'unknown');
      next();
    } catch {
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

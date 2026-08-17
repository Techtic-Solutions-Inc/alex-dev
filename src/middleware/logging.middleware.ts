import { Injectable, NestMiddleware } from '@nestjs/common';
import { NextFunction, Request, Response } from 'express';
import { logger } from '../config/logger.config';

@Injectable()
export class LoggingMiddleware implements NestMiddleware {
  use(request: Request, response: Response, next: NextFunction): void {
    const startedAt = process.hrtime.bigint();

    response.on('finish', () => {
      const durationMs = Number(process.hrtime.bigint() - startedAt) / 1_000_000;
      logger.info('HTTP request completed', {
        method: request.method,
        path: request.originalUrl,
        statusCode: response.statusCode,
        durationMs: Number(durationMs.toFixed(2)),
      });
    });

    next();
  }
}

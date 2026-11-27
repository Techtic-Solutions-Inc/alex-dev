import { Injectable, NestMiddleware } from '@nestjs/common';
import { NextFunction, Request, Response } from 'express';
import logger from '../services/logger.service';
import { RequestWithContext } from './request-context.middleware';

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  use(request: Request, response: Response, next: NextFunction): void {
    const startedAt = process.hrtime.bigint();
    const requestId = (request as RequestWithContext).requestId;

    response.on('finish', () => {
      const durationMs = Number(process.hrtime.bigint() - startedAt) / 1_000_000;
      const level = response.statusCode >= 500 ? 'error' : response.statusCode >= 400 ? 'warn' : 'info';
      logger.log(level, 'HTTP request completed', {
        requestId,
        event: { kind: 'event', category: 'web', type: 'access' },
        http: {
          method: request.method,
          path: request.originalUrl,
          status_code: response.statusCode,
          duration_ms: Number(durationMs.toFixed(2)),
        },
      });
    });

    next();
  }
}

import { Injectable, NestMiddleware } from '@nestjs/common';
import { randomUUID } from 'crypto';
import { NextFunction, Request, Response } from 'express';

export interface RequestWithContext extends Request {
  requestId: string;
}

@Injectable()
export class RequestContextMiddleware implements NestMiddleware {
  use(request: Request, response: Response, next: NextFunction): void {
    const headerId = request.headers['x-request-id'];
    const incoming = Array.isArray(headerId) ? headerId[0] : headerId;
    const requestId =
      typeof incoming === 'string' && incoming.trim().length > 0 && incoming.trim().length <= 128
        ? incoming.trim()
        : randomUUID();

    Object.assign(request, { requestId } satisfies Pick<RequestWithContext, 'requestId'>);
    response.setHeader('X-Request-Id', requestId);
    next();
  }
}
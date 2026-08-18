import { CallHandler, ExecutionContext, HttpStatus, Injectable, NestInterceptor } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { Observable, map } from 'rxjs';

interface EnvelopeBody {
  message?: string;
  data?: unknown;
}

@Injectable()
export class ResponseEnvelopeInterceptor implements NestInterceptor {
  constructor(private readonly reflector: Reflector) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const statusCode = this.reflector.get<number | undefined>('httpCode', context.getHandler());

    if (statusCode === HttpStatus.NO_CONTENT) {
      return next.handle();
    }

    return next.handle().pipe(
      map((body: unknown) => {
        const response = this.isEnvelopeBody(body) ? body : { data: body };
        return {
          success: true,
          message: response.message ?? 'Request completed successfully',
          data: 'data' in response && response.data !== undefined ? response.data : {},
        };
      }),
    );
  }

  private isEnvelopeBody(value: unknown): value is EnvelopeBody {
    return (
      typeof value === 'object' && value !== null && !Array.isArray(value) && ('message' in value || 'data' in value)
    );
  }
}

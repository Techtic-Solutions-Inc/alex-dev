import { CallHandler, ExecutionContext, Injectable, NestInterceptor } from '@nestjs/common';
import { Observable, map } from 'rxjs';

interface EnvelopeBody {
  message?: string;
  data?: unknown;
}

@Injectable()
export class ResponseEnvelopeInterceptor implements NestInterceptor {
  intercept(_context: ExecutionContext, next: CallHandler): Observable<unknown> {
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

import { CallHandler, ExecutionContext, HttpException as NestHttpException, Injectable, NestInterceptor } from '@nestjs/common';
import { Request, Response } from 'express';
import { Observable, catchError, tap, throwError } from 'rxjs';
import { ApmService } from '../apm/apm.service';
import { HttpException } from '../exceptions/http.exception';

@Injectable()
export class ApmInterceptor implements NestInterceptor {
  constructor(private readonly apmService: ApmService) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    if (context.getType() !== 'http') {
      return next.handle();
    }

    const http = context.switchToHttp();
    const request = http.getRequest<Request>();
    const startedAt = process.hrtime.bigint();
    const route = this.resolveRoute(request);

    return next.handle().pipe(
      tap(() => {
        const response = http.getResponse<Response>();
        this.record(request.method, route, response.statusCode, startedAt);
      }),
      catchError((error: unknown) => {
        const statusCode = this.resolveStatusCode(error);
        this.record(request.method, route, statusCode, startedAt, true);
        if (statusCode >= 500) {
          const message = error instanceof Error ? error.message : 'Unknown server error';
          this.apmService.recordError('http.unhandled', message);
        }
        return throwError(() => error);
      }),
    );
  }

  private record(method: string, route: string, statusCode: number, startedAt: bigint, error = false): void {
    const durationMs = Number(process.hrtime.bigint() - startedAt) / 1_000_000;
    this.apmService.recordHttpRequest({
      method,
      route,
      statusCode,
      durationMs: Number(durationMs.toFixed(2)),
      error,
    });
  }

  private resolveRoute(request: Request): string {
    const routePath = (request as Request & { route?: { path?: string } }).route?.path;
    if (routePath) {
      return routePath;
    }
    const [path] = request.originalUrl.split('?');
    return path ?? request.url;
  }

  private resolveStatusCode(error: unknown): number {
    if (error instanceof HttpException) {
      return error.status;
    }
    if (error instanceof NestHttpException) {
      return error.getStatus();
    }
    if (typeof error === 'object' && error !== null && 'getStatus' in error) {
      const getStatus = (error as { getStatus: () => number }).getStatus;
      if (typeof getStatus === 'function') {
        return getStatus.call(error);
      }
    }
    return 500;
  }
}
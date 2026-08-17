import { ArgumentsHost, Catch, ExceptionFilter, HttpException as NestHttpException, HttpStatus } from '@nestjs/common';
import { Request, Response } from 'express';
import { HttpException } from '../exceptions/http.exception';

interface ErrorPayload {
  code: string;
  details: Record<string, unknown> | null;
  message: string;
  status: number;
}

@Catch()
export class GlobalExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost): void {
    const response = host.switchToHttp().getResponse<Response>();
    const request = host.switchToHttp().getRequest<Request>();
    const error = this.toErrorPayload(exception);

    response.status(error.status).json({
      success: false,
      message: error.message,
      error: { code: error.code, details: error.details },
      path: request.url,
      timestamp: new Date().toISOString(),
    });
  }

  private toErrorPayload(exception: unknown): ErrorPayload {
    if (exception instanceof HttpException) {
      return {
        status: exception.status,
        message: exception.message,
        code: exception.code,
        details: exception.details,
      };
    }

    if (exception instanceof NestHttpException) {
      const status = exception.getStatus();
      const payload = exception.getResponse();
      const payloadObject = typeof payload === 'string' ? { message: payload } : payload;
      const message = this.messageFromPayload(payloadObject);
      const isValidationError =
        status === HttpStatus.UNPROCESSABLE_ENTITY || this.validationDetails(payloadObject) !== null;

      return {
        status,
        message: isValidationError ? 'Validation failed' : message,
        code: isValidationError ? 'VALIDATION_ERROR' : this.codeForStatus(status),
        details: isValidationError ? this.validationDetails(payloadObject) : null,
      };
    }

    return {
      status: HttpStatus.INTERNAL_SERVER_ERROR,
      message: 'An unexpected error occurred',
      code: 'INTERNAL_SERVER_ERROR',
      details: null,
    };
  }

  private messageFromPayload(payload: object): string {
    const value = Reflect.get(payload, 'message');
    return typeof value === 'string' ? value : 'Request failed';
  }

  private validationDetails(payload: object): Record<string, string[]> | null {
    const errors = Reflect.get(payload, 'errors');
    return typeof errors === 'object' && errors !== null ? (errors as Record<string, string[]>) : null;
  }

  private codeForStatus(status: number): string {
    const codes: Record<number, string> = {
      400: 'BAD_REQUEST',
      401: 'UNAUTHORIZED',
      403: 'FORBIDDEN',
      404: 'NOT_FOUND',
      409: 'CONFLICT',
      422: 'VALIDATION_ERROR',
    };
    return codes[status] ?? 'HTTP_ERROR';
  }
}

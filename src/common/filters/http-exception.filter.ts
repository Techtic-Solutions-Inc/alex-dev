import { ArgumentsHost, Catch, ExceptionFilter, HttpException, HttpStatus } from '@nestjs/common';
import { Request, Response } from 'express';

@Catch(HttpException)
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: HttpException, host: ArgumentsHost): void {
    const context = host.switchToHttp();
    const response = context.getResponse<Response>();
    const request = context.getRequest<Request>();
    const status = exception.getStatus();
    const payload = exception.getResponse();
    const payloadObject = typeof payload === 'string' ? { message: payload } : (payload as Record<string, unknown>);

    const message = this.messageFromPayload(payloadObject);
    const validationDetails = this.validationDetails(payloadObject);
    const isValidationError =
      status === HttpStatus.UNPROCESSABLE_ENTITY || status === HttpStatus.BAD_REQUEST || validationDetails !== null;

    response.status(status).json({
      success: false,
      message: isValidationError ? 'Validation failed' : message,
      error: {
        code: isValidationError ? 'VALIDATION_ERROR' : this.codeForStatus(status),
        details: isValidationError ? validationDetails : null,
      },
      path: request.url,
      timestamp: new Date().toISOString(),
    });
  }

  private messageFromPayload(payload: Record<string, unknown>): string {
    const value = payload.message;
    if (typeof value === 'string') {
      return value;
    }
    if (Array.isArray(value) && value.every((item) => typeof item === 'string')) {
      return value.join('; ');
    }
    return 'Request failed';
  }

  private validationDetails(payload: Record<string, unknown>): Record<string, string[]> | string[] | null {
    const errors = payload.errors;
    if (Array.isArray(errors) && errors.every((item) => typeof item === 'string')) {
      return errors;
    }
    if (typeof errors === 'object' && errors !== null) {
      return errors as Record<string, string[]>;
    }
    return null;
  }

  private codeForStatus(status: number): string {
    const codes: Record<number, string> = {
      [HttpStatus.BAD_REQUEST]: 'BAD_REQUEST',
      [HttpStatus.UNAUTHORIZED]: 'UNAUTHORIZED',
      [HttpStatus.FORBIDDEN]: 'FORBIDDEN',
      [HttpStatus.NOT_FOUND]: 'NOT_FOUND',
      [HttpStatus.CONFLICT]: 'CONFLICT',
      [HttpStatus.UNPROCESSABLE_ENTITY]: 'VALIDATION_ERROR',
    };
    return codes[status] ?? 'HTTP_ERROR';
  }
}

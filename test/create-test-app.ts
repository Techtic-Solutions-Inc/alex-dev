import { BadRequestException, HttpStatus, INestApplication, ValidationPipe } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { getConnectionToken } from '@nestjs/mongoose';
import { Test, TestingModule } from '@nestjs/testing';
import { ValidationError } from 'class-validator';
import { Connection } from 'mongoose';
import { HttpExceptionFilter } from '../src/common/filters/http-exception.filter';
import { GlobalExceptionFilter } from '../src/common/filters/global-exception.filter';
import { applySecurityHeaders } from '../src/common/helpers/security-headers.bootstrap';
import { ResponseEnvelopeInterceptor } from '../src/common/interceptors/response-envelope.interceptor';
import { registerPrometheusMetricsRoute } from '../src/common/apm/register-metrics-route';
import { resolveSecuritySettings } from '../src/config/security.config';
import { EmailVerificationService } from '../src/modules/auth/email-verification.service';
import { ensureMongoMemoryUri } from './mongodb-memory';

export const verificationTokens = new Map<string, string>();

const validationDetails = (errors: ValidationError[]): Record<string, string[]> =>
  errors.reduce<Record<string, string[]>>((details, error) => {
    const messages = Object.values(error.constraints ?? {});
    if (messages.length > 0) {
      details[error.property] = messages;
    }
    if (error.children?.length) {
      Object.assign(details, validationDetails(error.children));
    }
    return details;
  }, {});

export async function createTestApp(): Promise<INestApplication> {
  verificationTokens.clear();
  await ensureMongoMemoryUri();

  const { AppModule } = await import('../src/app.module');

  const moduleFixture: TestingModule = await Test.createTestingModule({
    imports: [AppModule],
  })
    .overrideProvider(EmailVerificationService)
    .useValue({
      sendVerificationEmail: jest.fn(async (email: string, _firstName: string, token: string) => {
        verificationTokens.set(email, token);
      }),
    })
    .compile();

  const app = moduleFixture.createNestApplication();
  app.setGlobalPrefix('api/v1');
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
      errorHttpStatusCode: HttpStatus.BAD_REQUEST,
      exceptionFactory: (errors) =>
        new BadRequestException({
          message: 'Validation failed',
          errors: validationDetails(errors),
        }),
    }),
  );
  app.useGlobalFilters(new GlobalExceptionFilter(), new HttpExceptionFilter());
  app.useGlobalInterceptors(new ResponseEnvelopeInterceptor(app.get(Reflector)));
  await app.init();

  const securitySettings = resolveSecuritySettings({
    NODE_ENV: process.env.NODE_ENV,
    TRUST_PROXY: process.env.TRUST_PROXY,
    FORCE_HTTPS: process.env.FORCE_HTTPS,
    SECURITY_HSTS_ENABLED: process.env.SECURITY_HSTS_ENABLED,
    SECURITY_HSTS_MAX_AGE_SECONDS: process.env.SECURITY_HSTS_MAX_AGE_SECONDS,
  });
  const expressInstance = app.getHttpAdapter().getInstance();
  if (securitySettings.trustProxy) {
    expressInstance.set('trust proxy', 1);
  }
  applySecurityHeaders(app, securitySettings);
  registerPrometheusMetricsRoute(app);

  const connection = app.get<Connection>(getConnectionToken());
  if (connection.readyState !== 1) {
    await connection.asPromise();
  }

  return app;
}

export async function clearUsers(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').deleteMany({});
  verificationTokens.clear();
}

export function uniqueEmail(prefix: string): string {
  return `${prefix}.${Date.now()}.${Math.random().toString(36).slice(2, 8)}@example.com`;
}

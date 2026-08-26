import { BadRequestException, HttpStatus, INestApplication, ValidationPipe } from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { getConnectionToken } from '@nestjs/mongoose';
import { Test, TestingModule } from '@nestjs/testing';
import { ValidationError } from 'class-validator';
import { Connection } from 'mongoose';
import { AppModule } from '../src/app.module';
import { GlobalExceptionFilter } from '../src/common/filters/global-exception.filter';
import { ResponseEnvelopeInterceptor } from '../src/common/interceptors/response-envelope.interceptor';
import { EmailVerificationService } from '../src/modules/auth/email-verification.service';

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
  app.setGlobalPrefix('api', { exclude: ['health'] });
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
  app.useGlobalFilters(new GlobalExceptionFilter());
  app.useGlobalInterceptors(new ResponseEnvelopeInterceptor(app.get(Reflector)));
  await app.init();
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

export async function clearVisitorHome(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('visitor_home_contents').deleteMany({});
  await connection.collection('visitor_home_subscriptions').deleteMany({});
}

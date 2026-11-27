import './common/apm/apm.bootstrap';
import { BadRequestException, HttpStatus, ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { Reflector } from '@nestjs/core';
import { ValidationError } from 'class-validator';
import { Request, Response } from 'express';
import { AppModule } from './app.module';
import logger from './common/services/logger.service';

const isMongoConnectionError = (error: unknown): boolean => {
  if (!(error instanceof Error)) {
    return false;
  }
  return (
    error.name === 'MongoServerSelectionError' ||
    error.message.includes('ECONNREFUSED') ||
    error.message.includes('Server selection timed out')
  );
};

const registerMongoConnectionGuards = (): void => {
  process.on('uncaughtException', (error: Error) => {
    if (isMongoConnectionError(error)) {
      logger.warn('MongoDB unavailable; process continues for liveness probes', { message: error.message });
      return;
    }
    throw error;
  });

  process.on('unhandledRejection', (reason: unknown) => {
    if (isMongoConnectionError(reason)) {
      logger.warn('MongoDB unavailable; process continues for liveness probes', {
        message: reason instanceof Error ? reason.message : String(reason),
      });
      return;
    }
  });
};
import { HttpExceptionFilter } from './common/filters/http-exception.filter';
import { GlobalExceptionFilter } from './common/filters/global-exception.filter';
import { ApmInterceptor } from './common/interceptors/apm.interceptor';
import { ResponseEnvelopeInterceptor } from './common/interceptors/response-envelope.interceptor';
import { ApmService } from './common/apm/apm.service';

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

async function bootstrap(): Promise<void> {
  registerMongoConnectionGuards();
  const app = await NestFactory.create(AppModule);
  const configService = app.get(ConfigService);
  const corsOrigin = configService.get<string>('CORS_ORIGIN')?.trim();
  const allowAllOrigins = !corsOrigin || corsOrigin === '*';

  app.setGlobalPrefix('api/v1');

  const expressInstance = app.getHttpAdapter().getInstance();
  expressInstance.get('/health', (_request: Request, response: Response) => {
    response.status(200).json({ status: 'UP' });
  });
  expressInstance.get('/', (_request: Request, response: Response) => {
    response.status(200).json({ status: 'UP' });
  });
  app.enableCors({
    origin: allowAllOrigins
      ? true
      : corsOrigin
          .split(',')
          .map((origin) => origin.trim())
          .filter(Boolean),
    credentials: true,
  });
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
  app.useGlobalInterceptors(
    new ResponseEnvelopeInterceptor(app.get(Reflector)),
    new ApmInterceptor(app.get(ApmService)),
  );

  const swaggerConfig = new DocumentBuilder()
    .setTitle('Backend API')
    .setDescription('REST API documentation for the backend service.')
    .setVersion('1.0.0')
    .addBearerAuth({ type: 'http', scheme: 'bearer', bearerFormat: 'JWT', description: 'Access JWT' }, 'access-token')
    .build();
  SwaggerModule.setup('api/docs', app, SwaggerModule.createDocument(app, swaggerConfig));

  const configuredPort = Number(configService.get<string>('PORT', '3000'));
  const port = Number.isInteger(configuredPort) && configuredPort >= 0 ? configuredPort : 3000;
  await app.listen(port);
}

void bootstrap();

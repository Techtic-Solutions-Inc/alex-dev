import './common/apm/apm.bootstrap';
import { BadRequestException, HttpStatus, ValidationPipe } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NestFactory } from '@nestjs/core';
import { DocumentBuilder, SwaggerModule } from '@nestjs/swagger';
import { Reflector } from '@nestjs/core';
import { ValidationError } from 'class-validator';
import { Request, Response } from 'express';
import { AppModule } from './app.module';
import { applySecurityHeaders } from './common/helpers/security-headers.bootstrap';
import logger from './common/services/logger.service';
import { resolveSecuritySettings } from './config/security.config';
import { buildHttpsOptions } from './config/tls.config';

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
import { registerPrometheusMetricsRoute } from './common/apm/register-metrics-route';

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
  const httpsOptions = buildHttpsOptions(process.env);
  const app = await NestFactory.create(AppModule, httpsOptions ? { httpsOptions } : undefined);
  const configService = app.get(ConfigService);
  const corsOrigin = configService.get<string>('CORS_ORIGIN')?.trim();
  const allowAllOrigins = !corsOrigin || corsOrigin === '*';

  const securityEnvironment: Record<string, string | undefined> = {
    NODE_ENV: configService.get<string>('NODE_ENV'),
    TRUST_PROXY: configService.get<string>('TRUST_PROXY'),
    FORCE_HTTPS: configService.get<string>('FORCE_HTTPS'),
    SECURITY_HSTS_ENABLED: configService.get<string>('SECURITY_HSTS_ENABLED'),
    SECURITY_HSTS_MAX_AGE_SECONDS: configService.get<string>('SECURITY_HSTS_MAX_AGE_SECONDS'),
  };
  let securitySettings = resolveSecuritySettings(securityEnvironment);
  if (httpsOptions && configService.get<string>('SECURITY_HSTS_ENABLED') === undefined) {
    securitySettings = { ...securitySettings, hstsEnabled: true };
  }

  app.setGlobalPrefix('api/v1');

  const expressInstance = app.getHttpAdapter().getInstance();
  if (securitySettings.trustProxy) {
    expressInstance.set('trust proxy', 1);
  }
  applySecurityHeaders(app, securitySettings);
  expressInstance.get('/health', (_request: Request, response: Response) => {
    response.status(200).json({ status: 'UP' });
  });
  expressInstance.get('/', (_request: Request, response: Response) => {
    response.status(200).json({ status: 'UP' });
  });

  registerPrometheusMetricsRoute(app);
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
  logger.info('HTTP server started', {
    port,
    tls: Boolean(httpsOptions),
    trustProxy: securitySettings.trustProxy,
    forceHttps: securitySettings.forceHttps,
  });
}

void bootstrap().catch((error: unknown) => {
  logger.error('Application bootstrap failed', {
    message: error instanceof Error ? error.message : String(error),
    stack: error instanceof Error ? error.stack : undefined,
  });
  process.exit(1);
});

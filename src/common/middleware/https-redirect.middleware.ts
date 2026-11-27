import { Injectable, NestMiddleware } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { NextFunction, Request, Response } from 'express';
import { resolveSecuritySettings } from '../../config/security.config';

/**
 * Redirects plain HTTP requests to HTTPS when FORCE_HTTPS is enabled and a proxy forwards X-Forwarded-Proto.
 */
@Injectable()
export class HttpsRedirectMiddleware implements NestMiddleware {
  private readonly forceHttps: boolean;

  constructor(configService: ConfigService) {
    const environment: Record<string, string | undefined> = {
      NODE_ENV: configService.get<string>('NODE_ENV'),
      FORCE_HTTPS: configService.get<string>('FORCE_HTTPS'),
      TRUST_PROXY: configService.get<string>('TRUST_PROXY'),
      SECURITY_HSTS_ENABLED: configService.get<string>('SECURITY_HSTS_ENABLED'),
      SECURITY_HSTS_MAX_AGE_SECONDS: configService.get<string>('SECURITY_HSTS_MAX_AGE_SECONDS'),
    };
    this.forceHttps = resolveSecuritySettings(environment).forceHttps;
  }

  use(request: Request, response: Response, next: NextFunction): void {
    if (!this.forceHttps) {
      next();
      return;
    }

    const forwardedProtoHeader = request.headers['x-forwarded-proto'];
    const forwardedProto = Array.isArray(forwardedProtoHeader) ? forwardedProtoHeader[0] : forwardedProtoHeader;

    if (typeof forwardedProto === 'string' && forwardedProto.toLowerCase() !== 'https') {
      const host = request.headers.host ?? 'localhost';
      const target = `https://${host}${request.originalUrl}`;
      response.redirect(301, target);
      return;
    }

    next();
  }
}
import { INestApplication } from '@nestjs/common';
import type { SecuritySettings } from '../../config/security.config';

/**
 * Applies baseline HTTP response hardening headers for the API process.
 * TLS termination may also occur at the ingress; enable HSTS here only when the app serves HTTPS directly.
 */
export const applySecurityHeaders = (app: INestApplication, settings: SecuritySettings): void => {
  const expressInstance = app.getHttpAdapter().getInstance();
  expressInstance.disable('x-powered-by');

  expressInstance.use(
    (_request: unknown, response: { setHeader: (name: string, value: string) => void }, next: () => void): void => {
      response.setHeader('X-Content-Type-Options', 'nosniff');
      response.setHeader('X-Frame-Options', 'DENY');
      response.setHeader('X-DNS-Prefetch-Control', 'off');
      response.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');
      response.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
      response.setHeader('Cross-Origin-Resource-Policy', 'same-site');
      response.setHeader('Cross-Origin-Opener-Policy', 'same-origin');
      response.setHeader(
        'Content-Security-Policy',
        "default-src 'self'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'; object-src 'none'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:",
      );

      if (settings.hstsEnabled) {
        response.setHeader(
          'Strict-Transport-Security',
          `max-age=${settings.hstsMaxAgeSeconds}; includeSubDomains; preload`,
        );
      }

      next();
    },
  );
};

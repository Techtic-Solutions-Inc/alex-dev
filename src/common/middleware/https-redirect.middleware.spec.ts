import { ConfigService } from '@nestjs/config';
import { HttpsRedirectMiddleware } from './https-redirect.middleware';

const createMiddleware = (overrides: Record<string, string | undefined> = {}): HttpsRedirectMiddleware => {
  const config = new ConfigService({
    NODE_ENV: 'production',
    ...overrides,
  });
  return new HttpsRedirectMiddleware(config);
};

describe('HttpsRedirectMiddleware', () => {
  it('redirects when FORCE_HTTPS is enabled and forwarded proto is http', () => {
    const middleware = createMiddleware({ FORCE_HTTPS: 'true', TRUST_PROXY: 'true' });
    const redirect = jest.fn();
    const request = {
      headers: { 'x-forwarded-proto': 'http', host: 'api.example.com' },
      originalUrl: '/api/v1/health',
    };

    middleware.use(request as never, { redirect } as never, jest.fn());

    expect(redirect).toHaveBeenCalledWith(301, 'https://api.example.com/api/v1/health');
  });

  it('continues when forwarded proto is already https', () => {
    const middleware = createMiddleware({ FORCE_HTTPS: 'true' });
    const next = jest.fn();
    const request = {
      headers: { 'x-forwarded-proto': 'https', host: 'api.example.com' },
      originalUrl: '/api/v1/health',
    };

    middleware.use(request as never, { redirect: jest.fn() } as never, next);

    expect(next).toHaveBeenCalled();
  });
});
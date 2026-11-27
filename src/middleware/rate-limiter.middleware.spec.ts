import { HttpStatus } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { JwtModule, JwtService } from '@nestjs/jwt';
import { Test, TestingModule } from '@nestjs/testing';
import { Request, Response } from 'express';
import { generateToken } from '../common/utils/token.util';
import { RateLimiterMiddleware } from './rate-limiter.middleware';

const requireTestJwtSecret = (): string => {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error('JWT_SECRET must be set for rate limiter middleware tests (see test/jest-common-setup.ts).');
  }
  return secret;
};

const mockResponse = (): Partial<Response> => {
  const response: Partial<Response> = {
    status: jest.fn().mockReturnThis(),
    json: jest.fn().mockReturnThis(),
    setHeader: jest.fn(),
  };
  return response;
};

const mockRequest = (overrides: Partial<Request> = {}): Request =>
  ({
    method: 'GET',
    originalUrl: '/api/v1/health',
    url: '/api/v1/health',
    ip: '203.0.113.10',
    socket: { remoteAddress: '203.0.113.10' },
    headers: {},
    ...overrides,
  }) as Request;

describe('RateLimiterMiddleware', () => {
  let middleware: RateLimiterMiddleware;
  let jwtService: JwtService;

  beforeEach(async () => {
    process.env.RATE_LIMIT_POINTS = '2';
    process.env.RATE_LIMIT_DURATION = '60';
    process.env.RATE_LIMIT_STRATEGY = 'fixed';

    const module: TestingModule = await Test.createTestingModule({
      imports: [
        ConfigModule.forRoot({ isGlobal: true, ignoreEnvFile: true }),
        JwtModule.register({
          secret: requireTestJwtSecret(),
        }),
      ],
      providers: [RateLimiterMiddleware],
    }).compile();

    middleware = module.get(RateLimiterMiddleware);
    jwtService = module.get(JwtService);
  });

  it('test_rate_limiting_success — calls next() while under the limit', async () => {
    const request = mockRequest();
    const response = mockResponse();
    const next = jest.fn();

    await middleware.use(request, response as Response, next);

    expect(next).toHaveBeenCalledTimes(1);
    expect(response.status).not.toHaveBeenCalled();
  });

  it('test_rate_limiting_exceeded — returns 429 when the IP bucket is full', async () => {
    const request = mockRequest();
    const response = mockResponse();
    const next = jest.fn();

    await middleware.use(request, response as Response, next);
    await middleware.use(request, response as Response, next);
    await middleware.use(request, response as Response, next);

    expect(next).toHaveBeenCalledTimes(2);
    expect(response.status).toHaveBeenCalledWith(HttpStatus.TOO_MANY_REQUESTS);
    expect(response.json).toHaveBeenCalledWith(
      expect.objectContaining({
        success: false,
        error: { code: 'RATE_LIMITED', details: null },
      }),
    );
  });

  it('buckets authenticated users separately from IP', async () => {
    const token = generateToken(jwtService, 'user-abc', 3600);
    const authedRequest = mockRequest({ headers: { authorization: `Bearer ${token}` } });
    const anonymousRequest = mockRequest({ ip: '203.0.113.99' });
    const response = mockResponse();
    const next = jest.fn();

    await middleware.use(authedRequest, response as Response, next);
    await middleware.use(authedRequest, response as Response, next);
    await middleware.use(anonymousRequest, response as Response, next);

    expect(next).toHaveBeenCalledTimes(3);
  });

  it('honours RATE_LIMIT_STRATEGY=sliding via config', async () => {
    const slidingModule: TestingModule = await Test.createTestingModule({
      imports: [
        ConfigModule.forRoot({
          isGlobal: true,
          ignoreEnvFile: true,
          load: [
            () => ({
              RATE_LIMIT_POINTS: '2',
              RATE_LIMIT_DURATION: '60',
              RATE_LIMIT_STRATEGY: 'sliding',
            }),
          ],
        }),
        JwtModule.register({ secret: requireTestJwtSecret() }),
      ],
      providers: [RateLimiterMiddleware],
    }).compile();

    const slidingMiddleware = slidingModule.get(RateLimiterMiddleware);
    const request = mockRequest({ ip: '198.51.100.1' });
    const response = mockResponse();
    const next = jest.fn();

    await slidingMiddleware.use(request, response as Response, next);
    await slidingMiddleware.use(request, response as Response, next);
    await slidingMiddleware.use(request, response as Response, next);

    expect(next).toHaveBeenCalledTimes(2);
    expect(response.status).toHaveBeenCalledWith(HttpStatus.TOO_MANY_REQUESTS);
  });
});
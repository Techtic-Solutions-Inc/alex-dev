import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';
import { RateLimiterMiddleware } from '../src/middleware/rate-limiter.middleware';

describe('RateLimiterMiddleware (e2e)', () => {
  let app: INestApplication;
  let jwtService: JwtService;
  let configService: ConfigService;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    jwtService = app.get<JwtService>(JwtService);
    configService = app.get<ConfigService>(ConfigService);
  });

  afterAll(async () => {
    await app.close();
  });

  it('should limit requests per user', async () => {
    const token = jwtService.sign({ sub: 'test-user' });

    for (let i = 0; i < 5; i++) {
      await request(app.getHttpServer()).get('/api/some-endpoint').set('Authorization', `Bearer ${token}`).expect(200);
    }

    const response = await request(app.getHttpServer())
      .get('/api/some-endpoint')
      .set('Authorization', `Bearer ${token}`)
      .expect(429);

    expect(response.body).toEqual({ error: 'RATE_LIMITED' });
  });

  it('should support configurable rate limiting strategies', async () => {
    configService.get = jest.fn().mockReturnValueOnce('sliding');
    const token = jwtService.sign({ sub: 'test-user' });

    await request(app.getHttpServer()).get('/api/some-endpoint').set('Authorization', `Bearer ${token}`).expect(200);

    // Additional tests for sliding window strategy can be added here
  });

  it('should return 403 for unauthorized users', async () => {
    await request(app.getHttpServer()).get('/api/some-endpoint').expect(403);
  });
});

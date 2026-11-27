import { Test, TestingModule } from '@nestjs/testing';
import { AuthService, SessionBootstrap } from '../auth/auth.service';
import { HealthController } from './health.controller';
import { HealthService } from './health.service';

const emptySession: SessionBootstrap = {
  status: 'UP',
  id: null,
  name: null,
  full_name: null,
  first_name: null,
  last_name: null,
  email: null,
  phone: null,
  token: null,
  bio: null,
  city: null,
  country: null,
  zip: null,
  address: null,
  image: null,
  password: null,
  profile: null,
};

describe('HealthController', () => {
  let controller: HealthController;
  let authService: Pick<AuthService, 'resolveSession'>;
  let healthService: Pick<HealthService, 'assertDatabaseReady'>;

  beforeEach(async () => {
    authService = {
      resolveSession: jest.fn().mockResolvedValue(emptySession),
    };
    healthService = {
      assertDatabaseReady: jest.fn(),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: HealthService, useValue: healthService },
      ],
    }).compile();

    controller = module.get<HealthController>(HealthController);
  });

  it('test_health_check', async () => {
    const result = await controller.check();

    expect(healthService.assertDatabaseReady).toHaveBeenCalledTimes(1);
    expect(authService.resolveSession).toHaveBeenCalledWith(undefined);
    expect(result).toEqual({
      message: 'API is healthy',
      data: emptySession,
    });
    expect(result.data.status).toBe('UP');
  });
});

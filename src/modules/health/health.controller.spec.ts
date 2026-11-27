import { Test, TestingModule } from '@nestjs/testing';
import { ApmService } from '../../common/apm/apm.service';
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
      assertDatabaseReady: jest.fn().mockResolvedValue(undefined),
    };

    const apmService: Pick<ApmService, 'getSystemHealthSnapshot'> = {
      getSystemHealthSnapshot: jest.fn().mockReturnValue({
        uptime_seconds: 10,
        memory_heap_used_mb: 50,
        memory_rss_mb: 80,
        event_loop_delay_ms: 0.5,
        apm_enabled: false,
        apm_provider: null,
      }),
    };

    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [
        { provide: AuthService, useValue: authService },
        { provide: HealthService, useValue: healthService },
        { provide: ApmService, useValue: apmService },
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
      data: {
        ...emptySession,
        system_health: {
          uptime_seconds: 10,
          memory_heap_used_mb: 50,
          memory_rss_mb: 80,
          event_loop_delay_ms: 0.5,
          apm_enabled: false,
          apm_provider: null,
        },
      },
    });
    expect(result.data.status).toBe('UP');
  });
});
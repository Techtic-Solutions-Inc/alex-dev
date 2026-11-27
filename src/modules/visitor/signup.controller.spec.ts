import { Test, TestingModule } from '@nestjs/testing';
import { VisitorSignupController } from './signup.controller';
import { VisitorSignupService } from './signup.service';

describe('VisitorSignupController', () => {
  let controller: VisitorSignupController;
  const service: jest.Mocked<Pick<VisitorSignupService, 'signup'>> = {
    signup: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [VisitorSignupController],
      providers: [{ provide: VisitorSignupService, useValue: service }],
    }).compile();

    controller = module.get(VisitorSignupController);
    jest.clearAllMocks();
  });

  it('test_signup_success', async () => {
    service.signup.mockResolvedValue({
      id: 'user-id',
      name: 'John Doe',
      full_name: 'John Doe',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      phone: null,
      email_verified: false,
      description: 'Please check your email to verify your address before signing in.',
      link: '/sign-in',
      error: null,
    });

    const result = await controller.signup({
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      password: 'StrongPassword123!',
      terms_accepted: true,
    });

    expect(service.signup).toHaveBeenCalled();
    expect(result.data.email).toBe('john.doe@example.com');
    expect(result.data.error).toBeNull();
  });

  it('test_signup_duplicate_email', async () => {
    service.signup.mockRejectedValue(new Error('duplicate'));
    await expect(
      controller.signup({
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'StrongPassword123!',
        terms_accepted: true,
      }),
    ).rejects.toThrow('duplicate');
  });

  it('test_signup_invalid_data', async () => {
    service.signup.mockRejectedValue(new Error('validation'));
    await expect(
      controller.signup({
        first_name: '',
        last_name: 'Doe',
        email: 'not-an-email',
        password: 'weak',
        terms_accepted: false,
      }),
    ).rejects.toThrow('validation');
  });
});

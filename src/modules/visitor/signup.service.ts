import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { Auth0AuthenticationService } from '../auth/auth0-authentication.service';
import { AuthService, RegisteredUser } from '../auth/auth.service';
import { SignupDto } from '../auth/dto/signup.dto';

export interface VisitorSignupUser extends RegisteredUser {
  description: string | null;
  link: string | null;
  error: null;
}

@Injectable()
export class VisitorSignupService {
  constructor(
    private readonly authService: AuthService,
    private readonly auth0AuthenticationService: Auth0AuthenticationService,
    private readonly configService: ConfigService,
  ) {}

  async signup(dto: SignupDto): Promise<VisitorSignupUser> {
    await this.auth0AuthenticationService.registerUser({
      email: dto.email,
      password: dto.password,
      first_name: dto.first_name,
      last_name: dto.last_name,
    });

    const user = await this.authService.signup(dto);
    return this.toVisitorSignupUser(user);
  }

  private toVisitorSignupUser(user: RegisteredUser): VisitorSignupUser {
    return {
      ...user,
      description: 'Please check your email to verify your address before signing in.',
      link: this.configService.get<string>('VISITOR_SIGN_IN_URL', '/sign-in'),
      error: null,
    };
  }
}

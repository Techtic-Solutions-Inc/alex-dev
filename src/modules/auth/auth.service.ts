// Import necessary modules
import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Auth0Service } from './auth0.service';
import { SessionRevocationService } from './session-revocation.service';

@Injectable()
export class AuthService {
  constructor(
    private readonly jwtService: JwtService,
    private readonly auth0Service: Auth0Service,
    private readonly sessionRevocationService: SessionRevocationService,
  ) {}

  async login(auth0Credentials: any) {
    // Validate Auth0 credentials
    const user = await this.auth0Service.validateUser(auth0Credentials);
    if (!user) {
      throw new Error('Invalid credentials');
    }

    // Issue local JWT after successful Auth0 validation
    const payload = { username: user.username, sub: user.id };
    const accessToken = this.jwtService.sign(payload);
    const refreshToken = this.jwtService.sign(payload, { expiresIn: '7d' });

    return { accessToken, refreshToken };
  }

  async logout(token: string) {
    // Revoke the local JWT token
    await this.sessionRevocationService.revokeAccessToken(token);
  }

  // Other methods...
}
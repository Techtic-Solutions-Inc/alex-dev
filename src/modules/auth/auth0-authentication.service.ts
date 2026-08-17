import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { HttpException } from '../../common/exceptions/http.exception';

interface Auth0TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type?: string;
}

interface Auth0ErrorResponse {
  error?: string;
  error_description?: string;
}

/**
 * Authenticates database-connection users through Auth0's OAuth token endpoint.
 * Auth0's resource owner password flow must be enabled for the configured client.
 */
@Injectable()
export class Auth0AuthenticationService {
  private readonly logger = new Logger(Auth0AuthenticationService.name);

  constructor(private readonly configService: ConfigService) {}

  isConfigured(): boolean {
    return Boolean(
      this.configService.get<string>('AUTH0_DOMAIN') &&
      this.configService.get<string>('AUTH0_CLIENT_ID') &&
      this.configService.get<string>('AUTH0_CLIENT_SECRET') &&
      this.configService.get<string>('AUTH0_CONNECTION'),
    );
  }

  async authenticate(email: string, password: string): Promise<Auth0TokenResponse> {
    if (!this.isConfigured()) {
      throw new HttpException(
        'Authentication is temporarily unavailable. Please try again later.',
        503,
        'AUTHENTICATION_UNAVAILABLE',
      );
    }

    const domain = this.configService
      .getOrThrow<string>('AUTH0_DOMAIN')
      .replace(/^https?:\/\//, '')
      .replace(/\/+$/, '');
    const body = new URLSearchParams({
      grant_type: 'http://auth0.com/oauth/grant-type/password-realm',
      client_id: this.configService.getOrThrow<string>('AUTH0_CLIENT_ID'),
      client_secret: this.configService.getOrThrow<string>('AUTH0_CLIENT_SECRET'),
      username: email,
      password,
      realm: this.configService.getOrThrow<string>('AUTH0_CONNECTION'),
      scope: this.configService.get<string>('AUTH0_SCOPE', 'openid profile email offline_access'),
    });
    const audience = this.configService.get<string>('AUTH0_AUDIENCE');
    if (audience) {
      body.set('audience', audience);
    }

    const endpoint = `https://${domain}/oauth/token`;
    for (let attempt = 0; attempt < 2; attempt += 1) {
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          headers: { 'content-type': 'application/x-www-form-urlencoded' },
          body,
          signal: AbortSignal.timeout(5_000),
        });

        const payload = (await response.json().catch(() => ({}))) as Auth0TokenResponse & Auth0ErrorResponse;
        if (response.ok && typeof payload.access_token === 'string' && payload.access_token.length > 0) {
          return payload;
        }

        if (response.status === 400 || response.status === 401 || response.status === 403) {
          throw new HttpException('Email or password is incorrect', 401, 'INVALID_CREDENTIALS');
        }

        if (response.status < 500 || attempt === 1) {
          this.logger.warn(`Auth0 token request failed with status ${response.status}`);
          throw new HttpException(
            'Authentication is temporarily unavailable. Please try again later.',
            503,
            'AUTHENTICATION_UNAVAILABLE',
          );
        }
      } catch (error) {
        if (error instanceof HttpException) {
          throw error;
        }
        if (attempt === 1) {
          this.logger.warn('Auth0 token request could not be completed');
          throw new HttpException(
            'Authentication is temporarily unavailable. Please try again later.',
            503,
            'AUTHENTICATION_UNAVAILABLE',
          );
        }
      }
    }

    throw new HttpException(
      'Authentication is temporarily unavailable. Please try again later.',
      503,
      'AUTHENTICATION_UNAVAILABLE',
    );
  }
}

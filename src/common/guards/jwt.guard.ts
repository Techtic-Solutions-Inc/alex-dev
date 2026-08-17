import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';
import { HttpException } from '../exceptions/http.exception';
import { TokenPayload } from '../utils/token.util';

export interface AuthenticatedRequest extends Request {
  user: TokenPayload;
}

@Injectable()
export class JwtAuthGuard implements CanActivate {
  constructor(private readonly jwtService: JwtService) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const token = this.extractBearerToken(request);

    try {
      request.user = this.jwtService.verify<TokenPayload>(token);
      if (request.user.tokenUse === 'refresh') {
        throw new HttpException('Authentication token is invalid or expired', 401, 'INVALID_TOKEN');
      }
      return true;
    } catch (error) {
      if (error instanceof HttpException) {
        throw error;
      }
      throw new HttpException('Authentication token is invalid or expired', 401, 'INVALID_TOKEN');
    }
  }

  private extractBearerToken(request: Request): string {
    const [scheme, token] = request.headers.authorization?.split(' ') ?? [];
    if (scheme !== 'Bearer' || !token) {
      throw new HttpException('Authentication is required', 401, 'AUTHENTICATION_REQUIRED');
    }
    return token;
  }
}

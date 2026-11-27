import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { HttpException } from '../../../common/exceptions/http.exception';
import { AuthenticatedRequest } from '../../../common/guards/jwt.guard';
import { TokenPayload } from '../../../common/utils/token.util';

/**
 * Blog detail reads require an authenticated Real Estate Professional session.
 * Missing or invalid credentials yield 403 (per product spec), not 401.
 */
@Injectable()
export class BlogDetailAccessGuard implements CanActivate {
  constructor(private readonly jwtService: JwtService) {}

  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const token = this.extractBearerToken(request);

    if (!token) {
      throw new HttpException('You are not authorized to view this blog post', 403, 'BLOG_ACCESS_FORBIDDEN');
    }

    try {
      const payload = this.jwtService.verify<TokenPayload>(token);
      if (payload.tokenUse === 'refresh') {
        throw new Error('refresh token not allowed');
      }
      request.user = payload;
      return true;
    } catch {
      throw new HttpException('You are not authorized to view this blog post', 403, 'BLOG_ACCESS_FORBIDDEN');
    }
  }

  private extractBearerToken(request: AuthenticatedRequest): string | null {
    const authorization = request.headers.authorization;
    if (!authorization?.startsWith('Bearer ')) {
      return null;
    }
    const token = authorization.slice('Bearer '.length).trim();
    return token.length > 0 ? token : null;
  }
}

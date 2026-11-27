import { JwtService } from '@nestjs/jwt';
import { Request } from 'express';
import { TokenPayload } from '../utils/token.util';

/**
 * Builds a stable client id for rate limiting.
 * Authenticated callers are bucketed by JWT `sub`; anonymous traffic falls back to IP.
 */
export function resolveRateLimitKey(request: Request, jwtService: JwtService): string {
  const authorization = request.headers.authorization;
  if (authorization?.startsWith('Bearer ')) {
    const token = authorization.slice('Bearer '.length).trim();
    if (token) {
      try {
        const payload = jwtService.verify<TokenPayload>(token);
        if (payload.tokenUse !== 'refresh' && payload.sub) {
          return `user:${payload.sub}`;
        }
      } catch {
        // Invalid tokens are treated as anonymous for rate limiting; route guards enforce auth.
      }
    }
  }

  const ip = request.ip ?? request.socket.remoteAddress ?? 'unknown';
  return `ip:${ip}`;
}
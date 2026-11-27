import { Injectable, NestMiddleware } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { NextFunction, Request, Response } from 'express';
import { TokenPayload } from '../utils/token.util';

@Injectable()
export class JwtMiddleware implements NestMiddleware {
  constructor(private readonly jwtService: JwtService) {}

  use(request: Request, _response: Response, next: NextFunction): void {
    const authorization = request.headers.authorization;
    if (authorization?.startsWith('Bearer ')) {
      const token = authorization.slice('Bearer '.length).trim();
      if (token) {
        try {
          const payload = this.jwtService.verify<TokenPayload>(token);
          if (payload.tokenUse !== 'refresh') {
            Object.assign(request, { user: payload });
          }
        } catch {
          // Route guards enforce authentication requirements.
        }
      }
    }
    next();
  }
}

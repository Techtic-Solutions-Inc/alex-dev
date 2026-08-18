import { JwtService } from '@nestjs/jwt';

export interface TokenPayload {
  sub: string;
  tokenUse?: 'access' | 'refresh';
}

export const generateToken = (
  jwtService: JwtService,
  userId: string,
  expiresIn: number,
  tokenUse: 'access' | 'refresh' = 'access',
): string =>
  jwtService.sign({ sub: userId, tokenUse } satisfies TokenPayload, {
    expiresIn,
  });

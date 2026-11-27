import { JwtService } from '@nestjs/jwt';
import { generateToken } from './token.util';

export class JwtUtil {
  constructor(private readonly jwtService: JwtService) {}

  generateAccessToken(userId: string, expiresInSeconds: number): string {
    return generateToken(this.jwtService, userId, expiresInSeconds, 'access');
  }

  generateRefreshToken(userId: string, expiresInSeconds: number): string {
    return generateToken(this.jwtService, userId, expiresInSeconds, 'refresh');
  }
}

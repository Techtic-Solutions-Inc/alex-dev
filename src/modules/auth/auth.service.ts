// Restored AuthService implementation from commit 042a063
import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { UserService } from '../user/user.service';
import { RegisterDto } from './dto/register.dto';
import { LoginDto } from './dto/login.dto';
import { TokenPair } from './interfaces/token-pair.interface';
import { User } from '../user/user.entity';
import * as bcrypt from 'bcrypt';

@Injectable()
export class AuthService {
  constructor(
    private readonly userService: UserService,
    private readonly jwtService: JwtService,
  ) {}

  async signup(registerDto: RegisterDto): Promise<User> {
    const hashedPassword = await this.hashPassword(registerDto.password);
    return this.userService.create({ ...registerDto, password: hashedPassword });
  }

  async login(loginDto: LoginDto): Promise<TokenPair> {
    const user = await this.userService.findByEmail(loginDto.email);
    if (!user || !(await this.verifyPassword(loginDto.password, user.password))) {
      throw new Error('Invalid credentials');
    }
    return this.generateTokenPair(user);
  }

  async verifyEmail(token: string): Promise<void> {
    // Implementation for email verification
  }

  async refresh(token: string): Promise<TokenPair> {
    // Implementation for token refresh
  }

  async verifyPassword(plainText: string, hashed: string): Promise<boolean> {
    return bcrypt.compare(plainText, hashed);
  }

  async hashPassword(password: string): Promise<string> {
    return bcrypt.hash(password, 10);
  }

  async generateTokenPair(user: User): Promise<TokenPair> {
    const payload = { email: user.email, sub: user.id };
    const accessToken = this.jwtService.sign(payload);
    const refreshToken = this.jwtService.sign(payload, { expiresIn: '7d' });
    return { accessToken, refreshToken };
  }

  async resolveSession(authorization: string): Promise<User> {
    // Implementation for resolving session
  }
}
import { createHash, randomBytes, scrypt as scryptCallback, timingSafeEqual } from 'crypto';
import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import { JwtService } from '@nestjs/jwt';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { promisify } from 'util';
import { HttpException } from '../../common/exceptions/http.exception';
import { generateToken, TokenPayload } from '../../common/utils/token.util';
import { Auth0AuthenticationService } from './auth0-authentication.service';
import { EmailVerificationService } from './email-verification.service';
import { LoginDto } from './dto/login.dto';
import { SignupDto } from './dto/signup.dto';
import { User, UserDocument } from './entities/user.schema';

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  tokenType: 'Bearer';
}

export interface RegisteredUser {
  id: string;
  name: string;
  full_name: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  email_verified: boolean;
}

export interface LoginResult {
  id: string;
  name: string;
  full_name: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  token: string;
  accessToken: string;
  refreshToken?: string;
  tokenType: 'Bearer';
}

export interface SessionBootstrap {
  status: 'UP';
  id: string | null;
  name: string | null;
  full_name: string | null;
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;
  token: string | null;
}

const scrypt = promisify(scryptCallback);

@Injectable()
export class AuthService {
  constructor(
    private readonly jwtService: JwtService,
    private readonly configService: ConfigService,
    @InjectModel(User.name) private readonly userModel: Model<User>,
    private readonly emailVerificationService: EmailVerificationService,
    private readonly auth0AuthenticationService: Auth0AuthenticationService,
  ) {}

  async signup(dto: SignupDto): Promise<RegisteredUser> {
    const verificationToken = randomBytes(32).toString('hex');
    const verificationTokenHash = this.hashToken(verificationToken);
    const passwordHash = await this.hashPassword(dto.password);

    let user: UserDocument;
    try {
      user = await this.userModel.create({
        first_name: dto.first_name,
        last_name: dto.last_name,
        email: dto.email,
        phone: dto.phone?.trim() ?? null,
        password_hash: passwordHash,
        terms_accepted: dto.terms_accepted,
        verification_token_hash: verificationTokenHash,
        verification_token_expires_at: new Date(Date.now() + this.verificationTokenTtlMs()),
      });
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw new HttpException('An account with this email address already exists', 409, 'EMAIL_ALREADY_EXISTS', {
          email: ['An account with this email address already exists'],
        });
      }
      throw error;
    }

    try {
      await this.emailVerificationService.sendVerificationEmail(user.email, user.first_name, verificationToken);
    } catch (error) {
      try {
        await this.userModel.deleteOne({ _id: user._id }).exec();
      } catch {
        // The original delivery error is safe to report; persistence errors remain internal.
      }

      if (error instanceof HttpException) {
        throw error;
      }

      throw new HttpException(
        'We could not send your verification email. Please try again.',
        500,
        'EMAIL_DELIVERY_FAILED',
      );
    }
    return this.toRegisteredUser(user);
  }

  async verifyEmail(token: string): Promise<RegisteredUser> {
    const tokenHash = this.hashToken(token);
    const user = await this.userModel
      .findOneAndUpdate(
        {
          verification_token_hash: tokenHash,
          verification_token_expires_at: { $gt: new Date() },
          email_verified: false,
        },
        {
          $set: { email_verified: true },
          $unset: { verification_token_hash: 1, verification_token_expires_at: 1 },
        },
        { returnDocument: 'after' },
      )
      .exec();

    if (!user) {
      throw new HttpException(
        'This email verification link is invalid or has expired',
        400,
        'INVALID_VERIFICATION_TOKEN',
      );
    }

    return this.toRegisteredUser(user);
  }

  async login(dto: LoginDto): Promise<LoginResult> {
    const user = await this.userModel.findOne({ email: dto.email }).select('+password_hash').exec();

    if (!user) {
      throw new HttpException('Email or password is incorrect', 401, 'INVALID_CREDENTIALS');
    }

    if (user.is_active === false) {
      throw new HttpException('This account is inactive. Please contact support for assistance.', 403, 'USER_INACTIVE');
    }

    if (this.auth0AuthenticationService.isConfigured()) {
      const auth0Tokens = await this.auth0AuthenticationService.authenticate(dto.email, dto.password);
      if (!user.email_verified) {
        throw new HttpException('Please verify your email address before signing in.', 403, 'EMAIL_NOT_VERIFIED');
      }

      return {
        ...this.toLoginUser(user),
        token: auth0Tokens.access_token,
        accessToken: auth0Tokens.access_token,
        ...(auth0Tokens.refresh_token ? { refreshToken: auth0Tokens.refresh_token } : {}),
        tokenType: 'Bearer',
      };
    }

    if (!(await this.verifyPassword(dto.password, user.password_hash))) {
      throw new HttpException('Email or password is incorrect', 401, 'INVALID_CREDENTIALS');
    }

    if (!user.email_verified) {
      throw new HttpException('Please verify your email address before signing in.', 403, 'EMAIL_NOT_VERIFIED');
    }

    const tokens = this.issueTokenPair(user._id.toString());
    return {
      ...this.toLoginUser(user),
      token: tokens.accessToken,
      ...tokens,
    };
  }

  async resolveSession(authorization?: string): Promise<SessionBootstrap> {
    const emptySession: SessionBootstrap = {
      status: 'UP',
      id: null,
      name: null,
      full_name: null,
      first_name: null,
      last_name: null,
      email: null,
      phone: null,
      token: null,
    };

    const token = this.extractOptionalBearerToken(authorization);
    if (!token) {
      return emptySession;
    }

    let payload: TokenPayload;
    try {
      payload = this.jwtService.verify<TokenPayload>(token, {
        secret: this.configService.getOrThrow<string>('JWT_SECRET'),
      });
    } catch {
      return emptySession;
    }

    if (!payload.sub || typeof payload.sub !== 'string' || payload.tokenUse === 'refresh') {
      return emptySession;
    }

    const user = await this.userModel.findById(payload.sub).exec();
    if (!user || user.is_active === false) {
      return emptySession;
    }

    const profile = this.toRegisteredUser(user);
    return {
      status: 'UP',
      id: profile.id,
      name: profile.name,
      full_name: profile.full_name,
      first_name: profile.first_name,
      last_name: profile.last_name,
      email: profile.email,
      phone: profile.phone,
      token,
    };
  }

  refresh(refreshToken: string): TokenPair {
    let payload: TokenPayload;
    try {
      payload = this.jwtService.verify<TokenPayload>(refreshToken, {
        secret: this.configService.getOrThrow<string>('JWT_SECRET'),
      });
    } catch {
      throw new HttpException('Refresh token is invalid or expired', 401, 'INVALID_REFRESH_TOKEN');
    }

    if (!payload.sub || typeof payload.sub !== 'string' || payload.tokenUse !== 'refresh') {
      throw new HttpException('Refresh token is invalid or expired', 401, 'INVALID_REFRESH_TOKEN');
    }

    return this.issueTokenPair(payload.sub);
  }

  private issueTokenPair(userId: string): TokenPair {
    return {
      accessToken: generateToken(this.jwtService, userId, this.expiryInSeconds('JWT_EXPIRY', 3600), 'access'),
      refreshToken: generateToken(
        this.jwtService,
        userId,
        this.expiryInSeconds('JWT_REFRESH_EXPIRY', 86400),
        'refresh',
      ),
      tokenType: 'Bearer',
    };
  }

  private expiryInSeconds(name: string, fallback: number): number {
    const configuredValue = this.configService.get<string>(name);
    if (!configuredValue || !/^\d+$/.test(configuredValue)) {
      return fallback;
    }

    const seconds = Number(configuredValue);
    return Number.isSafeInteger(seconds) && seconds > 0 ? seconds : fallback;
  }

  async hashPassword(password: string): Promise<string> {
    const salt = randomBytes(16);
    const derivedKey = (await scrypt(password, salt, 64)) as Buffer;
    return `scrypt$${salt.toString('hex')}$${derivedKey.toString('hex')}`;
  }

  async verifyPassword(password: string, storedHash: string | undefined): Promise<boolean> {
    if (typeof storedHash !== 'string') {
      return false;
    }

    const parts = storedHash.split('$');
    if (
      parts.length !== 3 ||
      parts[0] !== 'scrypt' ||
      !/^[a-f\d]{32}$/i.test(parts[1]) ||
      !/^[a-f\d]{128}$/i.test(parts[2])
    ) {
      return false;
    }

    const expectedHash = Buffer.from(parts[2], 'hex');
    const derivedKey = (await scrypt(password, Buffer.from(parts[1], 'hex'), expectedHash.length)) as Buffer;
    return timingSafeEqual(expectedHash, derivedKey);
  }

  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  private verificationTokenTtlMs(): number {
    const configuredHours = this.configService.get<string>('EMAIL_VERIFICATION_TOKEN_EXPIRY_HOURS');
    const hours = configuredHours && /^\d+$/.test(configuredHours) ? Number(configuredHours) : 24;
    return Number.isSafeInteger(hours) && hours > 0 ? hours * 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
  }

  private toRegisteredUser(user: UserDocument): RegisteredUser {
    return {
      id: user._id.toString(),
      name: `${user.first_name} ${user.last_name}`,
      full_name: `${user.first_name} ${user.last_name}`,
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone: user.phone ?? null,
      email_verified: user.email_verified,
    };
  }

  private toLoginUser(user: UserDocument): Omit<LoginResult, 'token' | 'accessToken' | 'refreshToken' | 'tokenType'> {
    return {
      id: user._id.toString(),
      name: `${user.first_name} ${user.last_name}`,
      full_name: `${user.first_name} ${user.last_name}`,
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone: user.phone ?? null,
    };
  }

  private extractOptionalBearerToken(authorization?: string): string | null {
    const [scheme, token] = authorization?.split(' ') ?? [];
    return scheme === 'Bearer' && token ? token : null;
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }
}

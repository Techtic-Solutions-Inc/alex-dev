import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { User, UserDocument } from './entities/user.schema';
import { RegisterDto } from './dto/register.dto';
import { TokenPair } from './interfaces/token-pair.interface';
import { RegisteredUser, LoginResult, SessionBootstrap } from './interfaces/auth.interfaces';

@Injectable()
export class AuthService {
  constructor(@InjectModel(User.name) private userModel: Model<UserDocument>) {}

  async register(dto: RegisterDto): Promise<RegisteredUser> {
    const passwordHash = await this.hashPassword(dto.password);
    const user = new this.userModel({
      first_name: dto.first_name,
      last_name: dto.last_name,
      email: dto.email,
      phone: dto.phone?.trim() ?? null,
      password_hash: passwordHash,
      terms_accepted: dto.terms_accepted,
      verification_token_hash: verificationTokenHash,
    });
    await user.save();
    return {
      id: user._id.toString(),
      name: `${user.first_name} ${user.last_name}`,
      full_name: `${user.first_name} ${user.last_name}`,
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone: user.phone,
      email_verified: user.email_verified,
    };
  }

  async login(email: string, password: string): Promise<LoginResult> {
    const user = await this.userModel.findOne({ email }).exec();
    if (!user || !(await this.comparePassword(password, user.password_hash))) {
      throw new Error('Invalid credentials');
    }
    const tokenPair = await this.generateTokenPair(user);
    return {
      id: user._id.toString(),
      name: `${user.first_name} ${user.last_name}`,
      full_name: `${user.first_name} ${user.last_name}`,
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      phone: user.phone,
      token: tokenPair.accessToken,
      accessToken: tokenPair.accessToken,
      refreshToken: tokenPair.refreshToken,
    };
  }

  async verifyEmail(token: string): Promise<void> {
    // Implementation for email verification
  }

  async getSessionBootstrap(): Promise<SessionBootstrap> {
    return {
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
  }

  private async hashPassword(password: string): Promise<string> {
    // Implementation for hashing password
  }

  private async comparePassword(password: string, hash: string): Promise<boolean> {
    // Implementation for comparing password
  }

  private async generateTokenPair(user: UserDocument): Promise<TokenPair> {
    // Implementation for generating token pair
  }
}
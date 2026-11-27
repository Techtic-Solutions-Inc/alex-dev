import { createHash } from 'crypto';
import { Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';
import { RevokedAccessToken, RevokedAccessTokenDocument } from './entities/revoked-access-token.schema';

@Injectable()
export class SessionRevocationService {
  constructor(
    private readonly jwtService: JwtService,
    @InjectModel(RevokedAccessToken.name)
    private readonly revokedTokenModel: Model<RevokedAccessTokenDocument>,
  ) {}

  async revokeAccessToken(token: string): Promise<void> {
    const decoded = this.jwtService.decode(token);
    if (
      typeof decoded !== 'object' ||
      decoded === null ||
      typeof Reflect.get(decoded, 'sub') !== 'string' ||
      Reflect.get(decoded, 'tokenUse') === 'refresh'
    ) {
      throw new HttpException('Authentication token is invalid or expired', 401, 'INVALID_TOKEN');
    }

    try {
      this.jwtService.verify(token);
    } catch {
      throw new HttpException('Authentication token is invalid or expired', 401, 'INVALID_TOKEN');
    }

    const exp = Reflect.get(decoded, 'exp');
    const expiresAt =
      typeof exp === 'number' && Number.isFinite(exp) ? new Date(exp * 1000) : new Date(Date.now() + 60 * 60 * 1000);
    const tokenHash = this.hashToken(token);
    const userId = Reflect.get(decoded, 'sub') as string;

    await this.revokedTokenModel
      .updateOne({ token_hash: tokenHash }, { $set: { token_hash: tokenHash, user_id: userId, expires_at: expiresAt } }, { upsert: true })
      .exec();
  }

  async isAccessTokenRevoked(token: string): Promise<boolean> {
    const tokenHash = this.hashToken(token);
    const revoked = await this.revokedTokenModel.exists({ token_hash: tokenHash }).exec();
    return Boolean(revoked);
  }

  private hashToken(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }
}
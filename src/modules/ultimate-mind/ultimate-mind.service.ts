import { HttpStatus, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';
import { logger } from '../../config/logger.config';
import { User, UserDocument } from '../auth/entities/user.schema';
import {
  AiCreditUsageItemDto,
  CreateUltimateMindAiCreditDto,
  UltimateMindAiCreditListDataDto,
  UltimateMindAiCreditRecordDataDto,
  UpdateUltimateMindAiCreditDto,
} from './dto/ultimate-mind.dto';
import {
  UltimateMindAiCreditRecord,
  UltimateMindAiCreditRecordDocument,
} from './entities/ultimate-mind-ai-credit-record.schema';

@Injectable()
export class UltimateMindService {
  constructor(
    @InjectModel(UltimateMindAiCreditRecord.name)
    private readonly aiCreditRecordModel: Model<UltimateMindAiCreditRecord>,
    @InjectModel(User.name) private readonly userModel: Model<User>,
  ) {}

  /**
   * Returns AI credit usage records visible to the requesting user along with profile header fields.
   */
  async listRecords(requestingUserId: string): Promise<UltimateMindAiCreditListDataDto> {
    const requestingUser = await this.getUserOrThrow(requestingUserId);
    const filter: Record<string, unknown> = { is_active: true };

    if (requestingUser.role !== 'admin') {
      filter.user_id = this.toObjectId(requestingUserId);
    }

    const records = await this.aiCreditRecordModel.find(filter).sort({ updatedAt: -1, createdAt: -1 }).exec();
    const linkedUsers = await this.loadUsersForRecords(records);

    return {
      ai_credit_usage: records.map((record) => {
        const linkedUser = linkedUsers.get(record.user_id.toString());
        return this.toUsageItem(record, linkedUser);
      }),
      full_name: this.toFullName(requestingUser),
      phone: requestingUser.phone ?? null,
    };
  }

  /**
   * Creates a new AI credit usage record and synchronizes credits on the linked user account.
   */
  async createRecord(
    adminUserId: string,
    dto: CreateUltimateMindAiCreditDto,
  ): Promise<UltimateMindAiCreditRecordDataDto> {
    await this.assertAdmin(adminUserId);

    const linkedUser = await this.getLinkedUserOrThrow(dto.user_id);
    await this.ensureNoActiveRecordForUser(dto.user_id);

    if (dto.usage > dto.limit) {
      throw new HttpException('Usage cannot exceed the credit limit', HttpStatus.UNPROCESSABLE_ENTITY, 'VALIDATION_ERROR', {
        usage: ['Usage cannot exceed the credit limit'],
        limit: ['Limit must be greater than or equal to usage'],
      });
    }

    let record: UltimateMindAiCreditRecordDocument;
    try {
      record = await this.aiCreditRecordModel.create({
        user_id: this.toObjectId(dto.user_id),
        usage: dto.usage,
        limit: dto.limit,
        full_name: dto.full_name.trim(),
        phone: dto.phone.trim(),
        is_active: true,
      });
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateRecordException();
      }
      throw error;
    }

    await this.syncUserCredits(linkedUser._id.toString(), record.usage, record.limit);

    logger.info('Ultimate Mind AI credit record created', {
      recordId: record._id.toString(),
      userId: dto.user_id,
      adminUserId,
    });

    return this.toRecordData(record, linkedUser);
  }

  /**
   * Updates an existing active AI credit usage record and synchronizes linked user credits.
   */
  async updateRecord(
    adminUserId: string,
    recordId: string,
    dto: UpdateUltimateMindAiCreditDto,
  ): Promise<UltimateMindAiCreditRecordDataDto> {
    await this.assertAdmin(adminUserId);

    const record = await this.findActiveRecordOrThrow(recordId);
    const linkedUser = await this.getLinkedUserOrThrow(record.user_id.toString());

    if (dto.usage !== undefined) {
      record.usage = dto.usage;
    }
    if (dto.limit !== undefined) {
      record.limit = dto.limit;
    }
    if (dto.full_name !== undefined) {
      record.full_name = dto.full_name.trim();
    }
    if (dto.phone !== undefined) {
      record.phone = dto.phone.trim();
    }

    if (record.usage > record.limit) {
      throw new HttpException('Usage cannot exceed the credit limit', HttpStatus.UNPROCESSABLE_ENTITY, 'VALIDATION_ERROR', {
        usage: ['Usage cannot exceed the credit limit'],
        limit: ['Limit must be greater than or equal to usage'],
      });
    }

    await record.save();
    await this.syncUserCredits(linkedUser._id.toString(), record.usage, record.limit);

    logger.info('Ultimate Mind AI credit record updated', {
      recordId: record._id.toString(),
      userId: record.user_id.toString(),
      adminUserId,
    });

    return this.toRecordData(record, linkedUser);
  }

  /**
   * Soft-deletes an active AI credit usage record.
   */
  async deleteRecord(adminUserId: string, recordId: string): Promise<void> {
    await this.assertAdmin(adminUserId);

    const record = await this.findActiveRecordOrThrow(recordId);
    record.is_active = false;
    await record.save();

    logger.info('Ultimate Mind AI credit record deleted', {
      recordId: record._id.toString(),
      userId: record.user_id.toString(),
      adminUserId,
    });
  }

  private async assertAdmin(userId: string): Promise<void> {
    const user = await this.userModel.findById(userId).select('role is_active').lean().exec();
    if (!user || user.is_active === false || user.role !== 'admin') {
      throw new HttpException(
        'You do not have permission to manage AI credit usage records',
        HttpStatus.FORBIDDEN,
        'ULTIMATE_MIND_ADMIN_REQUIRED',
      );
    }
  }

  private async getUserOrThrow(userId: string): Promise<UserDocument> {
    if (!Types.ObjectId.isValid(userId)) {
      throw new HttpException('Authentication token is invalid or expired', HttpStatus.UNAUTHORIZED, 'INVALID_TOKEN');
    }

    const user = await this.userModel.findById(userId).exec();
    if (!user || user.is_active === false) {
      throw new HttpException('Authentication token is invalid or expired', HttpStatus.UNAUTHORIZED, 'INVALID_TOKEN');
    }

    return user;
  }

  private async getLinkedUserOrThrow(userId: string): Promise<UserDocument> {
    if (!Types.ObjectId.isValid(userId)) {
      throw new HttpException('Linked user was not found', HttpStatus.NOT_FOUND, 'USER_NOT_FOUND');
    }

    const user = await this.userModel.findById(userId).exec();
    if (!user || user.is_active === false) {
      throw new HttpException('Linked user was not found', HttpStatus.NOT_FOUND, 'USER_NOT_FOUND');
    }

    return user;
  }

  private async findActiveRecordOrThrow(recordId: string): Promise<UltimateMindAiCreditRecordDocument> {
    if (!Types.ObjectId.isValid(recordId)) {
      throw new HttpException('AI credit usage record not found', HttpStatus.NOT_FOUND, 'ULTIMATE_MIND_AI_CREDIT_NOT_FOUND');
    }

    const record = await this.aiCreditRecordModel
      .findOne({
        _id: new Types.ObjectId(recordId),
        is_active: true,
      })
      .exec();

    if (!record) {
      throw new HttpException('AI credit usage record not found', HttpStatus.NOT_FOUND, 'ULTIMATE_MIND_AI_CREDIT_NOT_FOUND');
    }

    return record;
  }

  private async ensureNoActiveRecordForUser(userId: string): Promise<void> {
    const existing = await this.aiCreditRecordModel
      .exists({
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (existing) {
      throw this.duplicateRecordException();
    }
  }

  private async syncUserCredits(userId: string, usage: number, limit: number): Promise<void> {
    await this.userModel.updateOne(
      { _id: this.toObjectId(userId) },
      {
        $set: {
          ai_credits_used: usage,
          ai_credits_total: limit,
        },
      },
    );
  }

  private async loadUsersForRecords(
    records: UltimateMindAiCreditRecordDocument[],
  ): Promise<Map<string, UserDocument>> {
    const userIds = [...new Set(records.map((record) => record.user_id.toString()))];
    if (userIds.length === 0) {
      return new Map();
    }

    const users = await this.userModel
      .find({ _id: { $in: userIds.map((id) => new Types.ObjectId(id)) } })
      .exec();

    return new Map(users.map((user) => [user._id.toString(), user]));
  }

  private toUsageItem(
    record: UltimateMindAiCreditRecordDocument,
    linkedUser: UserDocument | undefined,
  ): AiCreditUsageItemDto {
    return {
      id: record._id.toString(),
      user: linkedUser ? this.toFullName(linkedUser) : record.full_name,
      usage: record.usage,
      limit: record.limit,
    };
  }

  private toRecordData(
    record: UltimateMindAiCreditRecordDocument,
    linkedUser: UserDocument,
  ): UltimateMindAiCreditRecordDataDto {
    return {
      ...this.toUsageItem(record, linkedUser),
      full_name: record.full_name,
      phone: record.phone,
    };
  }

  private toFullName(user: Pick<User, 'first_name' | 'last_name'>): string {
    return `${user.first_name} ${user.last_name}`.trim();
  }

  private toObjectId(value: string): Types.ObjectId {
    return new Types.ObjectId(value);
  }

  private duplicateRecordException(): HttpException {
    return new HttpException(
      'An active AI credit usage record already exists for this user',
      HttpStatus.CONFLICT,
      'ULTIMATE_MIND_AI_CREDIT_ALREADY_EXISTS',
      {
        user_id: ['An active AI credit usage record already exists for this user'],
      },
    );
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }
}

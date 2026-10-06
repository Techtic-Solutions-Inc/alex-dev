import { Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { isValidObjectId, Model, Types } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';
import { AuthService } from '../auth/auth.service';
import { User, UserDocument } from '../auth/entities/user.schema';
import {
  ChangePasswordDto,
  ContentGeneratedItemDto,
  ContentGeneratedResponseDataDto,
  CreateProfileContentDto,
  DownloadHistoryItemDto,
  DownloadsResponseDataDto,
  GetDownloadsQueryDto,
  ProfileAddressDto,
  ProfileResponseDataDto,
  ProfileSummaryDto,
  RedownloadDto,
  RedownloadResponseDataDto,
  UpdateProfileContentDto,
  UpdateProfileDto,
} from './dto/profile.dto';
import { ProfileContent, ProfileContentDocument } from './entities/profile-content.schema';
import { ProfileDownload, ProfileDownloadDocument } from './entities/profile-download.schema';
import { ProfileContentAnalyticsService } from './profile-content-analytics.service';
import { UltimateMindService } from '../ultimate-mind/ultimate-mind.service';

@Injectable()
export class ProfileService {
  constructor(
    @InjectModel(User.name) private readonly userModel: Model<User>,
    @InjectModel(ProfileDownload.name) private readonly profileDownloadModel: Model<ProfileDownload>,
    @InjectModel(ProfileContent.name) private readonly profileContentModel: Model<ProfileContent>,
    private readonly authService: AuthService,
    private readonly profileContentAnalyticsService: ProfileContentAnalyticsService,
    private readonly ultimateMindService: UltimateMindService,
  ) {}

  async getProfile(userId: string): Promise<ProfileResponseDataDto> {
    const user = await this.findUserById(userId);
    return this.toProfileResponse(user);
  }

  async updateProfile(userId: string, dto: UpdateProfileDto): Promise<ProfileResponseDataDto> {
    const user = await this.findUserById(userId);

    const normalizedEmail = dto.email.trim().toLowerCase();
    const phone = this.normalizeNullableString(dto.phone);
    const mobileNumber = this.normalizeNullableString(dto.mobile_number) ?? phone;
    const bio = this.normalizeNullableString(dto.bio);
    const description = this.normalizeNullableString(dto.description) ?? bio;

    const duplicateUser = await this.userModel
      .findOne({
        email: normalizedEmail,
        _id: { $ne: user._id },
      })
      .select('_id')
      .lean()
      .exec();

    if (duplicateUser) {
      throw new HttpException('Another account already uses this email address', 409, 'EMAIL_ALREADY_EXISTS', {
        email: ['Another account already uses this email address'],
      });
    }

    user.first_name = dto.first_name.trim();
    user.last_name = dto.last_name.trim();
    user.email = normalizedEmail;
    user.phone = phone ?? mobileNumber;
    user.mobile_number = mobileNumber ?? phone;
    user.bio = bio;
    user.description = description;
    user.time_zone = this.normalizeNullableString(dto.time_zone);
    user.street = this.normalizeNullableString(dto.street);
    user.country = this.normalizeNullableString(dto.country);
    user.state = this.normalizeNullableString(dto.state);
    user.city = this.normalizeNullableString(dto.city);
    user.zip = this.normalizeNullableString(dto.zip);
    user.image = this.normalizeNullableString(dto.image);
    user.link = this.normalizeNullableString(dto.link);

    try {
      await user.save();
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw new HttpException('Another account already uses this email address', 409, 'EMAIL_ALREADY_EXISTS', {
          email: ['Another account already uses this email address'],
        });
      }
      throw error;
    }

    return this.toProfileResponse(user);
  }

  async changePassword(userId: string, dto: ChangePasswordDto): Promise<void> {
    if (dto.current_password === dto.new_password) {
      throw new HttpException(
        'New password must be different from the current password',
        422,
        'PASSWORD_REUSE_NOT_ALLOWED',
        {
          new_password: ['New password must be different from the current password'],
        },
      );
    }

    if (dto.new_password !== dto.confirm_password) {
      throw new HttpException('Password confirmation does not match', 422, 'PASSWORD_CONFIRMATION_MISMATCH', {
        confirm_password: ['Password confirmation does not match'],
      });
    }

    const user = await this.findUserById(userId, true);
    const passwordMatches = await this.authService.verifyPassword(dto.current_password, user.password_hash);
    if (!passwordMatches) {
      throw new HttpException('Current password is incorrect', 401, 'INVALID_CURRENT_PASSWORD');
    }

    user.password_hash = await this.authService.hashPassword(dto.new_password);
    await user.save();
  }

  async getDownloads(userId: string, query: GetDownloadsQueryDto): Promise<DownloadsResponseDataDto> {
    const user = await this.findUserById(userId);
    const { page, limit } = query;
    const objectId = this.toObjectId(userId);
    const filter = { user_id: objectId, is_active: true };
    const skip = (page - 1) * limit;

    const [downloads, total] = await Promise.all([
      this.profileDownloadModel
        .find(filter)
        .sort({ last_downloaded_at: -1, createdAt: -1 })
        .skip(skip)
        .limit(limit)
        .exec(),
      this.profileDownloadModel.countDocuments(filter).exec(),
    ]);

    const fullName = `${user.first_name} ${user.last_name}`.trim();
    const phone = user.phone ?? user.mobile_number ?? null;
    const totalPages = total === 0 ? 0 : Math.ceil(total / limit);

    return {
      id: 'profile_downloads',
      title: 'Download history',
      name: fullName,
      full_name: fullName,
      phone,
      message: 'Download history retrieved successfully',
      description: 'Active download history for the authenticated user',
      profile: {
        id: user._id.toString(),
        name: fullName,
        full_name: fullName,
        phone,
      },
      downloads: downloads.map((download) => this.toDownloadHistoryItem(download)),
      pagination: {
        page,
        limit,
        total,
        total_pages: totalPages,
        has_next_page: total > page * limit,
        has_previous_page: page > 1 && total > 0,
      },
      link: null,
      error: null,
    };
  }

  async redownload(userId: string, dto: RedownloadDto): Promise<RedownloadResponseDataDto> {
    await this.findUserById(userId);

    const download = await this.profileDownloadModel
      .findOne({
        _id: this.toObjectId(dto.download_id),
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (!download) {
      throw new HttpException('Download record was not found', 404, 'DOWNLOAD_NOT_FOUND');
    }

    download.last_downloaded_at = new Date();
    await download.save();

    return {
      id: 'profile_download_redownload',
      title: 'Re-download ready',
      name: download.title,
      full_name: dto.full_name.trim(),
      phone: dto.phone.trim(),
      message: 'Re-download prepared successfully',
      description: 'The selected file is ready to be downloaded again',
      download: this.toDownloadHistoryItem(download),
      link: download.link ?? null,
      error: null,
    };
  }

  async getGeneratedContent(userId: string): Promise<ContentGeneratedResponseDataDto> {
    const user = await this.findUserById(userId);
    const contents = await this.profileContentModel
      .find({ user_id: this.toObjectId(userId), is_active: true })
      .sort({ updatedAt: -1, createdAt: -1 })
      .exec();

    void this.profileContentAnalyticsService.trackEvent(userId, 'profile_content_viewed');

    const fullName = `${user.first_name} ${user.last_name}`.trim();
    const phone = user.phone ?? user.mobile_number ?? null;

    return {
      id: 'profile_content_generated',
      title: 'Content history',
      message: 'Generated content retrieved successfully',
      description: 'Generated content history for the authenticated user',
      name: fullName,
      full_name: fullName,
      phone,
      profile: {
        id: user._id.toString(),
        name: fullName,
        full_name: fullName,
        phone,
      },
      contents: contents.map((content) => this.toContentItem(content)),
      ai_credit_usage: {
        total_ai_credits: user.ai_credits_total,
        used_ai_credits: user.ai_credits_used,
        remaining_ai_credits: Math.max(user.ai_credits_total - user.ai_credits_used, 0),
      },
      link: null,
      error: null,
    };
  }

  async createGeneratedContent(userId: string, dto: CreateProfileContentDto): Promise<ContentGeneratedItemDto> {
    const user = await this.findUserById(userId);

    if (!user.ai_generation_enabled) {
      throw new HttpException(
        'You are not allowed to use AI content generation features',
        403,
        'AI_CONTENT_GENERATION_FORBIDDEN',
      );
    }

    if (user.ai_credits_used >= user.ai_credits_total) {
      throw new HttpException('You have reached your AI credit limit', 409, 'AI_CREDIT_LIMIT_REACHED');
    }

    const content = await this.profileContentModel.create({
      user_id: this.toObjectId(userId),
      title: dto.title.trim(),
      description: dto.description.trim(),
      full_name: dto.full_name.trim(),
      phone: dto.phone.trim(),
      link: this.normalizeNullableString(dto.link),
      is_active: true,
    });

    user.ai_credits_used += 1;
    await user.save();
    void this.ultimateMindService.syncUsageFromUser(userId);

    void this.profileContentAnalyticsService.trackEvent(userId, 'profile_content_created', content._id.toString());

    return this.toContentItem(content);
  }

  async updateGeneratedContent(
    userId: string,
    contentId: string,
    dto: UpdateProfileContentDto,
  ): Promise<ContentGeneratedItemDto> {
    await this.findUserById(userId);

    const content = await this.profileContentModel
      .findOne({
        _id: this.toObjectId(contentId, 'content_id'),
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (!content) {
      throw new HttpException('Generated content was not found', 404, 'CONTENT_NOT_FOUND');
    }

    content.title = dto.title.trim();
    content.description = dto.description.trim();
    content.full_name = dto.full_name.trim();
    content.phone = dto.phone.trim();
    content.link = this.normalizeNullableString(dto.link);
    await content.save();

    void this.profileContentAnalyticsService.trackEvent(userId, 'profile_content_updated', content._id.toString());

    return this.toContentItem(content);
  }

  async deleteGeneratedContent(userId: string, contentId: string): Promise<void> {
    await this.findUserById(userId);

    const content = await this.profileContentModel
      .findOne({
        _id: this.toObjectId(contentId, 'content_id'),
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (!content) {
      throw new HttpException('Generated content was not found', 404, 'CONTENT_NOT_FOUND');
    }

    content.is_active = false;
    await content.save();

    void this.profileContentAnalyticsService.trackEvent(userId, 'profile_content_deleted', content._id.toString());
  }

  private async findUserById(userId: string, includePasswordHash = false): Promise<UserDocument> {
    if (!isValidObjectId(userId)) {
      throw new HttpException('User profile was not found', 404, 'USER_NOT_FOUND');
    }

    const query = this.userModel.findById(userId);
    if (includePasswordHash) {
      query.select('+password_hash');
    }

    const user = await query.exec();
    if (!user || user.is_active === false) {
      throw new HttpException('User profile was not found', 404, 'USER_NOT_FOUND');
    }

    return user as UserDocument;
  }

  private toProfileResponse(user: UserDocument): ProfileResponseDataDto {
    const fullName = `${user.first_name} ${user.last_name}`.trim();
    const bio = user.bio ?? null;
    const description = user.description ?? bio;
    const addressDetails: ProfileAddressDto = {
      street: user.street ?? null,
      city: user.city ?? null,
      state: user.state ?? null,
      zip: user.zip ?? null,
      country: user.country ?? null,
    };
    const profile: ProfileSummaryDto = {
      bio,
      description,
      image: user.image ?? null,
      name: fullName,
    };

    return {
      id: user._id.toString(),
      name: fullName,
      full_name: fullName,
      first_name: user.first_name,
      last_name: user.last_name,
      email: user.email,
      mobile_number: user.mobile_number ?? user.phone ?? null,
      phone: user.phone ?? user.mobile_number ?? null,
      bio,
      description,
      time_zone: user.time_zone ?? null,
      street: addressDetails.street,
      country: addressDetails.country,
      state: addressDetails.state,
      city: addressDetails.city,
      zip: addressDetails.zip,
      address: this.formatAddress(addressDetails),
      profile,
      address_details: addressDetails,
      image: user.image ?? null,
      password: null,
      link: user.link ?? null,
      error: null,
    };
  }

  private toDownloadHistoryItem(download: ProfileDownloadDocument): DownloadHistoryItemDto {
    return {
      id: download._id.toString(),
      title: download.title,
      name: download.title,
      file_type: download.file_type,
      file_size: download.file_size,
      last_downloaded: download.last_downloaded_at.toISOString().slice(0, 10),
      downloaded_at: download.last_downloaded_at.toISOString(),
      status: 'active',
      link: download.link ?? null,
      message: 'Download available for re-download',
      description: download.description ?? `${download.title} (${download.file_type}, ${download.file_size})`,
      error: null,
    };
  }

  private toContentItem(content: ProfileContentDocument): ContentGeneratedItemDto {
    return {
      id: content._id.toString(),
      content_id: content._id.toString(),
      title: content.title,
      description: content.description,
      created_at: content.createdAt.toISOString(),
      updated_at: content.updatedAt.toISOString(),
      full_name: content.full_name,
      phone: content.phone,
      profile: {
        id: content.user_id.toString(),
        name: content.full_name,
        full_name: content.full_name,
        phone: content.phone,
      },
      link: content.link ?? null,
      error: null,
    };
  }

  private formatAddress(address: ProfileAddressDto): string | null {
    const lineOne = address.street?.trim();
    const locality = [address.city, address.state, address.zip].filter(
      (part) => typeof part === 'string' && part.trim().length > 0,
    );
    const parts = [lineOne, locality.length > 0 ? locality.join(', ').replace(', ,', ',') : null, address.country]
      .filter((part) => typeof part === 'string' && part.trim().length > 0)
      .map((part) => part!.trim());

    return parts.length > 0 ? parts.join(', ') : null;
  }

  private normalizeNullableString(value: string | null | undefined): string | null {
    if (typeof value !== 'string') {
      return null;
    }

    const trimmed = value.trim();
    return trimmed.length > 0 ? trimmed : null;
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }

  private toObjectId(value: string, fieldName = 'id'): Types.ObjectId {
    if (!Types.ObjectId.isValid(value)) {
      throw new HttpException('Validation failed', 422, 'VALIDATION_ERROR', {
        [fieldName]: [`${fieldName} must be a valid MongoDB ObjectId`],
      });
    }

    return new Types.ObjectId(value);
  }
}

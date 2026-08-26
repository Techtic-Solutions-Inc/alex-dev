import { HttpStatus, Injectable, Logger } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';
import {
  VisitorHomeContentItemResponseDto,
  VisitorHomeLeadResponseDto,
  VisitorHomeSearchDataDto,
  VisitorHomeSearchQueryDto,
  VisitorHomeSubscribeDto,
  VisitorHomeTermsAcceptanceDto,
} from './dto/visitor-home.dto';
import { VisitorHomeAnalyticsService } from './visitor-home-analytics.service';
import { VisitorHomeContent, VisitorHomeContentDocument } from './entities/visitor-home-content.schema';
import { VisitorHomeSubscription, VisitorHomeSubscriptionDocument } from './entities/visitor-home-subscription.schema';

/**
 * Public Visitor Home use cases: content search, marketing subscribe, and terms acceptance.
 */
@Injectable()
export class VisitorHomeService {
  private readonly logger = new Logger(VisitorHomeService.name);

  constructor(
    @InjectModel(VisitorHomeContent.name) private readonly contentModel: Model<VisitorHomeContent>,
    @InjectModel(VisitorHomeSubscription.name) private readonly subscriptionModel: Model<VisitorHomeSubscription>,
    private readonly visitorHomeAnalyticsService: VisitorHomeAnalyticsService,
  ) {}

  /**
   * Searches active public marketing content for the visitor Home screen.
   */
  async searchContent(query: VisitorHomeSearchQueryDto): Promise<VisitorHomeSearchDataDto> {
    const page = query.page ?? 1;
    const limit = query.limit ?? 10;
    const skip = (page - 1) * limit;
    const filter = this.buildContentFilter(query);

    const [items, total] = await Promise.all([
      this.contentModel.find(filter).sort({ updatedAt: -1, createdAt: -1 }).skip(skip).limit(limit).exec(),
      this.contentModel.countDocuments(filter).exec(),
    ]);

    void this.visitorHomeAnalyticsService.trackEvent('visitor', 'visitor_home_searched', {
      search_query: query.q?.trim() ?? null,
    });

    return {
      items: items.map((item) => this.toContentResponse(item)),
      pagination: {
        page,
        limit,
        total,
        total_pages: total === 0 ? 0 : Math.ceil(total / limit),
        has_next_page: total > page * limit,
        has_previous_page: page > 1 && total > 0,
      },
    };
  }

  /**
   * Creates or upgrades a marketing subscription. Duplicate subscribed emails return 409.
   */
  async subscribe(dto: VisitorHomeSubscribeDto): Promise<VisitorHomeLeadResponseDto> {
    const email = dto.email.trim().toLowerCase();
    const names = this.resolveNames(dto.full_name, dto.first_name, dto.last_name);
    const phone = this.resolvePhone(dto.phone, dto.phone_number);
    this.assertSubscribeIdentity(names.full_name, phone);
    const now = new Date();

    const existing = await this.findSubscriptionByEmail(email);
    if (existing?.subscribed) {
      throw this.duplicateSubscriptionException();
    }

    let subscription: VisitorHomeSubscriptionDocument;
    try {
      if (existing) {
        existing.full_name = names.full_name;
        existing.first_name = names.first_name;
        existing.last_name = names.last_name;
        existing.phone = phone;
        existing.terms_accepted = true;
        existing.subscribed = true;
        existing.terms_accepted_at = existing.terms_accepted_at ?? now;
        existing.subscribed_at = now;
        subscription = await existing.save();
      } else {
        subscription = await this.subscriptionModel.create({
          full_name: names.full_name,
          first_name: names.first_name,
          last_name: names.last_name,
          email,
          phone,
          terms_accepted: true,
          subscribed: true,
          terms_accepted_at: now,
          subscribed_at: now,
        });
      }
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateSubscriptionException();
      }
      throw error;
    }

    this.logger.log(`Visitor home subscription created for ${email}`);
    void this.visitorHomeAnalyticsService.trackEvent(email, 'visitor_home_subscribed');
    return this.toLeadResponse(subscription);
  }

  /**
   * Records Privacy Policy and Terms of Service acceptance. Idempotent for repeat submissions.
   */
  async acceptTerms(dto: VisitorHomeTermsAcceptanceDto): Promise<VisitorHomeLeadResponseDto> {
    const email = dto.email.trim().toLowerCase();
    const names = this.resolveNames(dto.full_name, dto.first_name, dto.last_name);
    const phone = this.resolvePhone(dto.phone, dto.phone_number);
    const now = new Date();

    const existing = await this.findSubscriptionByEmail(email);
    const setFields: Record<string, unknown> = {
      terms_accepted: true,
      terms_accepted_at: now,
    };

    if (names.full_name) {
      setFields.full_name = names.full_name;
      setFields.first_name = names.first_name;
      setFields.last_name = names.last_name;
    }
    if (phone) {
      setFields.phone = phone;
    }

    let subscription: VisitorHomeSubscriptionDocument | null;
    try {
      if (existing) {
        Object.assign(existing, setFields);
        subscription = await existing.save();
      } else {
        subscription = await this.subscriptionModel.create({
          email,
          full_name: names.full_name,
          first_name: names.first_name,
          last_name: names.last_name,
          phone,
          terms_accepted: true,
          subscribed: false,
          terms_accepted_at: now,
          subscribed_at: null,
        });
      }
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        const raced = await this.findSubscriptionByEmail(email);
        if (raced) {
          Object.assign(raced, setFields);
          subscription = await raced.save();
        } else {
          throw error;
        }
      } else {
        throw error;
      }
    }

    if (!subscription) {
      throw new HttpException(
        'Unable to record terms acceptance',
        HttpStatus.INTERNAL_SERVER_ERROR,
        'INTERNAL_SERVER_ERROR',
      );
    }

    this.logger.log(`Visitor home terms accepted for ${email}`);
    void this.visitorHomeAnalyticsService.trackEvent(email, 'visitor_home_terms_accepted');
    return this.toLeadResponse(subscription);
  }

  /**
   * Builds the Mongo filter for public Home content search.
   */
  private buildContentFilter(query: VisitorHomeSearchQueryDto): Record<string, unknown> {
    const filter: Record<string, unknown> = { is_active: true };

    if (query.category) {
      filter.category = { $regex: this.escapeRegex(query.category.trim()), $options: 'i' };
    }

    if (query.q) {
      const searchRegex = new RegExp(this.escapeRegex(query.q.trim()), 'i');
      filter.$or = [
        { title: searchRegex },
        { description: searchRegex },
        { category: searchRegex },
        { tags: searchRegex },
      ];
    }

    return filter;
  }

  /**
   * Looks up a visitor lead by case-insensitive email.
   */
  private async findSubscriptionByEmail(email: string): Promise<VisitorHomeSubscriptionDocument | null> {
    return this.subscriptionModel.findOne({ email }).collation({ locale: 'en', strength: 2 }).exec();
  }

  /**
   * Maps a public content document to the frontend Home search contract.
   */
  private toContentResponse(item: VisitorHomeContentDocument): VisitorHomeContentItemResponseDto {
    return {
      id: item._id.toString(),
      name: item.title,
      title: item.title,
      description: item.description,
      link: item.link,
      image: item.image_url,
      image_url: item.image_url,
      category: item.category,
      tags: item.tags,
      full_name: null,
      first_name: null,
      last_name: null,
      email: null,
      phone: null,
      phone_number: null,
      error: null,
      is_active: item.is_active,
      created_at: item.createdAt.toISOString(),
      updated_at: item.updatedAt.toISOString(),
    };
  }

  /**
   * Maps a visitor lead to the frontend Home form contract.
   */
  private toLeadResponse(subscription: VisitorHomeSubscriptionDocument): VisitorHomeLeadResponseDto {
    const names = this.resolveNames(subscription.full_name, subscription.first_name, subscription.last_name);
    return {
      id: subscription._id.toString(),
      name: names.full_name,
      full_name: names.full_name,
      first_name: names.first_name,
      last_name: names.last_name,
      email: subscription.email,
      phone: subscription.phone,
      phone_number: subscription.phone,
      link: null,
      description: null,
      terms_accepted: subscription.terms_accepted,
      subscribed: subscription.subscribed,
      error: null,
      created_at: subscription.createdAt.toISOString(),
      updated_at: subscription.updatedAt.toISOString(),
    };
  }

  /**
   * Resolves display and split name fields from Figma full_name or first/last name inputs.
   */
  private resolveNames(
    fullName?: string | null,
    firstName?: string | null,
    lastName?: string | null,
  ): { full_name: string; first_name: string | null; last_name: string | null } {
    const first = firstName?.trim() || null;
    const last = lastName?.trim() || null;
    const explicitFull = fullName?.trim() || '';

    if (first || last) {
      const composed = `${first ?? ''} ${last ?? ''}`.trim();
      return {
        full_name: explicitFull || composed,
        first_name: first,
        last_name: last,
      };
    }

    if (!explicitFull) {
      return { full_name: '', first_name: null, last_name: null };
    }

    const parts = explicitFull.split(/\s+/);
    return {
      full_name: explicitFull,
      first_name: parts[0] ?? null,
      last_name: parts.length > 1 ? parts.slice(1).join(' ') : null,
    };
  }

  /**
   * Resolves phone from the Figma phone field or the frontend phone_number alias.
   */
  private resolvePhone(phone?: string | null, phoneNumber?: string | null): string | null {
    const resolved = phone?.trim() || phoneNumber?.trim() || '';
    return resolved.length > 0 ? resolved : null;
  }

  /**
   * Builds the 409 response used when a visitor email is already subscribed.
   */
  private duplicateSubscriptionException(): HttpException {
    return new HttpException('This email address is already subscribed', HttpStatus.CONFLICT, 'EMAIL_ALREADY_EXISTS', {
      email: ['This email address is already subscribed'],
    });
  }

  /**
   * Ensures a marketing subscription includes a display name and phone number.
   */
  private assertSubscribeIdentity(fullName: string, phone: string | null): void {
    if (!fullName) {
      throw new HttpException('Validation failed', HttpStatus.BAD_REQUEST, 'VALIDATION_ERROR', {
        full_name: ['full_name is required'],
      });
    }
    if (!phone) {
      throw new HttpException('Validation failed', HttpStatus.BAD_REQUEST, 'VALIDATION_ERROR', {
        phone: ['phone is required'],
      });
    }
  }
  /**
   * Escapes user search input before compiling a regular expression.
   */
  private escapeRegex(value: string): string {
    return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  /**
   * Detects MongoDB duplicate-key errors from a unique email index.
   */
  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }
}

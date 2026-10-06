import { HttpStatus, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';
import { User, UserDocument } from '../auth/entities/user.schema';
import { CalendarService } from '../calendar/calendar.service';
import {
  AskDashboardQuestionDto,
  CreateAnnouncementDto,
  DashboardAnalyticsResponseDto,
  DashboardAnnouncementResponseDto,
  DashboardOverviewDataDto,
  DashboardQuestionResponseDataDto,
} from './dto/dashboard.dto';
import { DashboardAnnouncement, DashboardAnnouncementDocument } from './entities/dashboard-announcement.schema';
import { DashboardAnalyticsService } from './dashboard-analytics.service';
import { UltimateMindService } from '../ultimate-mind/ultimate-mind.service';

@Injectable()
export class DashboardService {
  constructor(
    @InjectModel(DashboardAnnouncement.name)
    private readonly dashboardAnnouncementModel: Model<DashboardAnnouncement>,
    @InjectModel(User.name)
    private readonly userModel: Model<User>,
    private readonly calendarService: CalendarService,
    private readonly dashboardAnalyticsService: DashboardAnalyticsService,
    private readonly ultimateMindService: UltimateMindService,
  ) {}

  async getOverview(userId: string): Promise<DashboardOverviewDataDto> {
    const [user, announcements, contentCalendar, analytics] = await Promise.all([
      this.getUserOrThrow(userId),
      this.listAnnouncements(userId),
      this.calendarService.listActiveEntries(userId),
      this.getAnalytics(userId),
    ]);

    if (
      announcements.length === 0 &&
      contentCalendar.length === 0 &&
      analytics.analytics_data.content_generated === 0
    ) {
      throw new HttpException(
        'Dashboard data was not found for this user',
        HttpStatus.NOT_FOUND,
        'DASHBOARD_DATA_NOT_FOUND',
      );
    }

    void this.dashboardAnalyticsService.trackEvent(userId, 'dashboard_viewed', {
      announcements_count: announcements.length,
      content_calendar_count: contentCalendar.length,
    });

    return {
      profile: {
        id: user._id.toString(),
        full_name: this.toFullName(user),
        email: user.email,
        phone: user.phone ?? null,
      },
      analytics,
      announcements,
      content_calendar: contentCalendar,
      status: 'active',
      error: null,
      link: null,
      description: 'Dashboard overview retrieved successfully',
    };
  }

  async listAnnouncements(userId: string): Promise<DashboardAnnouncementResponseDto[]> {
    await this.getUserOrThrow(userId);

    const announcements = await this.dashboardAnnouncementModel
      .find({ user_id: this.toObjectId(userId) })
      .sort({ createdAt: -1 })
      .exec();

    void this.dashboardAnalyticsService.trackEvent(userId, 'dashboard_announcements_viewed', {
      announcements_count: announcements.length,
    });

    return announcements.map((announcement) => this.toAnnouncementResponse(announcement));
  }

  async createAnnouncement(userId: string, dto: CreateAnnouncementDto): Promise<DashboardAnnouncementResponseDto> {
    await this.getUserOrThrow(userId);

    let announcement: DashboardAnnouncementDocument;
    try {
      announcement = await this.dashboardAnnouncementModel.create({
        user_id: this.toObjectId(userId),
        announcement_title: dto.announcement_title.trim(),
        announcement_content: dto.announcement_content.trim(),
        full_name: dto.full_name.trim(),
        email: dto.email.trim().toLowerCase(),
        phone: dto.phone.trim(),
        link: dto.link?.trim() ?? null,
        status: 'active',
      });
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw new HttpException(
          'An announcement with this title already exists',
          HttpStatus.CONFLICT,
          'ANNOUNCEMENT_TITLE_ALREADY_EXISTS',
          { announcement_title: ['An announcement with this title already exists'] },
        );
      }
      throw error;
    }

    void this.dashboardAnalyticsService.trackEvent(userId, 'dashboard_announcement_created', {
      announcement_id: announcement._id.toString(),
    });

    return this.toAnnouncementResponse(announcement);
  }

  async getAnalytics(userId: string): Promise<DashboardAnalyticsResponseDto> {
    const user = await this.getUserOrThrow(userId);
    const announcementCount = await this.dashboardAnnouncementModel
      .countDocuments({ user_id: this.toObjectId(userId) })
      .exec();

    void this.dashboardAnalyticsService.trackEvent(userId, 'dashboard_analytics_viewed', {
      content_generated: user.ai_credits_used,
      downloads: announcementCount,
    });

    return {
      id: 'dashboard_analytics',
      status: 'active',
      description: 'Dashboard analytics retrieved successfully',
      link: null,
      error: null,
      analytics_data: {
        content_generated: user.ai_credits_used,
        downloads: announcementCount,
        current_ai_credits: user.ai_credits_used,
        total_ai_credits: user.ai_credits_total,
        remaining_ai_credits: Math.max(user.ai_credits_total - user.ai_credits_used, 0),
      },
      full_name: this.toFullName(user),
      email: user.email,
      phone: user.phone ?? null,
    };
  }

  async askQuestion(userId: string, dto: AskDashboardQuestionDto): Promise<DashboardQuestionResponseDataDto> {
    const user = await this.getUserOrThrow(userId);

    if (!user.ai_generation_enabled) {
      throw new HttpException(
        'You are not allowed to use AI content generation features',
        HttpStatus.FORBIDDEN,
        'AI_CONTENT_GENERATION_FORBIDDEN',
      );
    }

    if (user.ai_credits_used >= user.ai_credits_total) {
      throw new HttpException('You have reached your AI credit limit', HttpStatus.CONFLICT, 'AI_CREDIT_LIMIT_REACHED');
    }

    user.ai_credits_used += 1;
    await user.save();
    void this.ultimateMindService.syncUsageFromUser(userId);

    void this.dashboardAnalyticsService.trackEvent(userId, 'dashboard_question_asked', {
      credits_used: 1,
      remaining_ai_credits: Math.max(user.ai_credits_total - user.ai_credits_used, 0),
    });

    const responseMessage = this.generateQuestionResponse(dto.message);

    return {
      id: `generated_question_${user._id.toString()}`,
      status: 'created',
      title: 'AI assistant response',
      message: responseMessage,
      description: responseMessage,
      link: null,
      error: null,
      credits_used: 1,
      remaining_ai_credits: Math.max(user.ai_credits_total - user.ai_credits_used, 0),
    };
  }

  private async getUserOrThrow(userId: string): Promise<UserDocument> {
    const user = await this.userModel.findById(this.toObjectId(userId)).exec();

    if (!user || user.is_active === false) {
      throw new HttpException('User not found', HttpStatus.NOT_FOUND, 'USER_NOT_FOUND');
    }

    return user;
  }

  private toAnnouncementResponse(announcement: DashboardAnnouncementDocument): DashboardAnnouncementResponseDto {
    return {
      id: announcement._id.toString(),
      announcement_title: announcement.announcement_title,
      announcement_content: announcement.announcement_content,
      title: announcement.announcement_title,
      message: announcement.announcement_content,
      description: announcement.announcement_content,
      full_name: announcement.full_name,
      email: announcement.email,
      phone: announcement.phone,
      link: announcement.link ?? null,
      status: announcement.status,
      error: null,
      created_at: announcement.createdAt.toISOString(),
      updated_at: announcement.updatedAt.toISOString(),
    };
  }

  private generateQuestionResponse(message: string): string {
    const prompt = message.trim();
    return `Suggested response for "${prompt}": highlight the property value, add a local market angle, and end with a clear call to action.`;
  }

  private toFullName(user: UserDocument): string {
    return `${user.first_name} ${user.last_name}`.trim();
  }

  private toObjectId(value: string): Types.ObjectId {
    if (!Types.ObjectId.isValid(value)) {
      throw new HttpException('Validation failed', HttpStatus.UNPROCESSABLE_ENTITY, 'VALIDATION_ERROR', {
        id: ['id must be a valid MongoDB ObjectId'],
      });
    }

    return new Types.ObjectId(value);
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }
}

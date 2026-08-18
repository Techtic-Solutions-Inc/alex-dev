import { HttpStatus, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';
import {
  ContentCalendarEntryResponseDto,
  CreateContentCalendarEntryDto,
  UpdateContentCalendarEntryDto,
} from './dto/content-calendar.dto';
import { ContentCalendarEntry, ContentCalendarEntryDocument } from './entities/content-calendar-entry.schema';
import { CalendarAnalyticsService } from './calendar-analytics.service';

@Injectable()
export class CalendarService {
  constructor(
    @InjectModel(ContentCalendarEntry.name)
    private readonly contentCalendarEntryModel: Model<ContentCalendarEntry>,
    private readonly calendarAnalyticsService: CalendarAnalyticsService,
  ) {}

  async listActiveEntries(userId: string): Promise<ContentCalendarEntryResponseDto[]> {
    const entries = await this.contentCalendarEntryModel
      .find({ user_id: this.toObjectId(userId), is_active: true })
      .sort({ date: 1, createdAt: 1 })
      .exec();

    void this.calendarAnalyticsService.trackEvent(userId, 'content_calendar_viewed');

    return entries.map((entry) => this.toResponse(entry));
  }

  async createEntry(userId: string, dto: CreateContentCalendarEntryDto): Promise<ContentCalendarEntryResponseDto> {
    const normalizedTitle = dto.title.trim();
    const normalizedDate = this.normalizeToUtcMidnight(new Date(dto.date));

    await this.ensureNoDuplicate(userId, normalizedTitle, normalizedDate);

    let entry: ContentCalendarEntryDocument;
    try {
      entry = await this.contentCalendarEntryModel.create({
        user_id: this.toObjectId(userId),
        title: normalizedTitle,
        date: normalizedDate,
        content: dto.content.trim(),
        description: dto.content.trim(),
        full_name: dto.full_name.trim(),
        phone: dto.phone.trim(),
        link: dto.link?.trim() ?? null,
        is_active: true,
      });
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateEntryException();
      }
      throw error;
    }

    void this.calendarAnalyticsService.trackEvent(userId, 'content_calendar_created', entry._id.toString());

    return this.toResponse(entry);
  }

  async updateEntry(
    userId: string,
    entryId: string,
    dto: UpdateContentCalendarEntryDto,
  ): Promise<ContentCalendarEntryResponseDto> {
    const entry = await this.findOwnedActiveEntry(userId, entryId);
    const nextTitle = dto.title?.trim() ?? entry.title;
    const nextDate = dto.date ? this.normalizeToUtcMidnight(new Date(dto.date)) : entry.date;

    await this.ensureNoDuplicate(userId, nextTitle, nextDate, entry._id.toString());

    entry.title = nextTitle;
    entry.date = nextDate;
    if (dto.content !== undefined) {
      entry.content = dto.content.trim();
    }
    if (dto.description !== undefined) {
      entry.description = dto.description.trim();
    } else if (dto.content !== undefined) {
      entry.description = dto.content.trim();
    }
    if (dto.full_name !== undefined) {
      entry.full_name = dto.full_name.trim();
    }
    if (dto.phone !== undefined) {
      entry.phone = dto.phone.trim();
    }
    if (dto.link !== undefined) {
      entry.link = dto.link === null ? null : dto.link.trim();
    }

    try {
      await entry.save();
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateEntryException();
      }
      throw error;
    }

    void this.calendarAnalyticsService.trackEvent(userId, 'content_calendar_updated', entry._id.toString());

    return this.toResponse(entry);
  }

  async deleteEntry(userId: string, entryId: string): Promise<void> {
    const entry = await this.findOwnedActiveEntry(userId, entryId);
    entry.is_active = false;
    await entry.save();

    void this.calendarAnalyticsService.trackEvent(userId, 'content_calendar_deleted', entry._id.toString());
  }

  private async ensureNoDuplicate(userId: string, title: string, date: Date, excludedId?: string): Promise<void> {
    const query: Record<string, unknown> = {
      user_id: this.toObjectId(userId),
      title,
      date,
      is_active: true,
    };

    if (excludedId) {
      query._id = { $ne: this.toObjectId(excludedId) };
    }

    const duplicate = await this.contentCalendarEntryModel.exists(query);
    if (duplicate) {
      throw this.duplicateEntryException();
    }
  }

  private async findOwnedActiveEntry(userId: string, entryId: string): Promise<ContentCalendarEntryDocument> {
    const objectId = this.toObjectId(entryId, 'CONTENT_ENTRY_NOT_FOUND');
    const entry = await this.contentCalendarEntryModel
      .findOne({
        _id: objectId,
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (!entry) {
      throw new HttpException('Content entry not found', HttpStatus.NOT_FOUND, 'CONTENT_ENTRY_NOT_FOUND');
    }

    return entry;
  }

  private duplicateEntryException(): HttpException {
    return new HttpException(
      'A content entry with this title already exists on the selected date',
      HttpStatus.CONFLICT,
      'CONTENT_ENTRY_ALREADY_EXISTS',
      {
        title: ['A content entry with this title already exists on the selected date'],
        date: ['A content entry with this title already exists on the selected date'],
      },
    );
  }

  private toObjectId(value: string, invalidCode = 'VALIDATION_ERROR'): Types.ObjectId {
    if (!Types.ObjectId.isValid(value)) {
      if (invalidCode === 'CONTENT_ENTRY_NOT_FOUND') {
        throw new HttpException('Content entry not found', HttpStatus.NOT_FOUND, 'CONTENT_ENTRY_NOT_FOUND');
      }

      throw new HttpException('Validation failed', HttpStatus.UNPROCESSABLE_ENTITY, invalidCode, {
        id: ['id must be a valid MongoDB ObjectId'],
      });
    }

    return new Types.ObjectId(value);
  }

  private toResponse(entry: ContentCalendarEntryDocument): ContentCalendarEntryResponseDto {
    return {
      id: entry._id.toString(),
      title: entry.title,
      date: entry.date.toISOString(),
      content: entry.content,
      description: entry.description,
      full_name: entry.full_name,
      phone: entry.phone,
      link: entry.link ?? null,
      error: null,
      is_active: entry.is_active,
      created_at: entry.createdAt.toISOString(),
      updated_at: entry.updatedAt.toISOString(),
    };
  }

  private normalizeToUtcMidnight(date: Date): Date {
    const normalized = new Date(date);
    normalized.setUTCHours(0, 0, 0, 0);
    return normalized;
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }
}

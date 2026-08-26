import { HttpStatus, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { HttpException } from '../../common/exceptions/http.exception';
import {
  ContentLibraryItemResponseDto,
  ContentLibraryListDataDto,
  ContentLibrarySearchQueryDto,
  CreateContentLibraryItemDto,
  UpdateContentLibraryItemDto,
} from './dto/content-library.dto';
import { ContentLibraryAnalyticsService } from './content-library-analytics.service';
import { ContentLibraryItem, ContentLibraryItemDocument } from './entities/content-library-item.schema';

@Injectable()
export class ContentLibraryService {
  constructor(
    @InjectModel(ContentLibraryItem.name) private readonly contentLibraryItemModel: Model<ContentLibraryItem>,
    private readonly contentLibraryAnalyticsService: ContentLibraryAnalyticsService,
  ) {}

  async listItems(userId: string, query: ContentLibrarySearchQueryDto): Promise<ContentLibraryListDataDto> {
    const data = await this.queryItems(userId, query);
    void this.contentLibraryAnalyticsService.trackEvent(userId, 'content_library_viewed', undefined, query.q?.trim());
    return data;
  }

  async searchItems(userId: string, query: ContentLibrarySearchQueryDto): Promise<ContentLibraryListDataDto> {
    const data = await this.queryItems(userId, query);
    void this.contentLibraryAnalyticsService.trackEvent(userId, 'content_library_searched', undefined, query.q?.trim());
    return data;
  }

  async createItem(userId: string, dto: CreateContentLibraryItemDto): Promise<ContentLibraryItemResponseDto> {
    const normalizedTitle = dto.title.trim();
    const normalizedCategory = dto.category.trim();

    await this.ensureNoDuplicate(userId, normalizedTitle, normalizedCategory);

    let item: ContentLibraryItemDocument;
    try {
      item = await this.contentLibraryItemModel.create({
        user_id: this.toObjectId(userId),
        title: normalizedTitle,
        description: dto.description.trim(),
        image_url: dto.image_url.trim(),
        link: dto.link.trim(),
        category: normalizedCategory,
        tags: this.normalizeTags(dto.tags),
        full_name: dto.full_name.trim(),
        phone: dto.phone.trim(),
        is_active: true,
      });
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateItemException();
      }
      throw error;
    }

    void this.contentLibraryAnalyticsService.trackEvent(userId, 'content_library_created', item._id.toString());
    return this.toResponse(item);
  }

  async getItem(userId: string, itemId: string): Promise<ContentLibraryItemResponseDto> {
    const item = await this.findOwnedActiveItem(userId, itemId);
    void this.contentLibraryAnalyticsService.trackEvent(userId, 'content_library_opened', item._id.toString());
    return this.toResponse(item);
  }

  async updateItem(
    userId: string,
    itemId: string,
    dto: UpdateContentLibraryItemDto,
  ): Promise<ContentLibraryItemResponseDto> {
    const item = await this.findOwnedActiveItem(userId, itemId);

    const nextTitle = dto.title?.trim() ?? item.title;
    const nextCategory = dto.category?.trim() ?? item.category;
    await this.ensureNoDuplicate(userId, nextTitle, nextCategory, item._id.toString());

    if (dto.title !== undefined) {
      item.title = nextTitle;
    }
    if (dto.description !== undefined) {
      item.description = dto.description.trim();
    }
    if (dto.image_url !== undefined) {
      item.image_url = dto.image_url.trim();
    }
    if (dto.link !== undefined) {
      item.link = dto.link.trim();
    }
    if (dto.category !== undefined) {
      item.category = nextCategory;
    }
    if (dto.tags !== undefined) {
      item.tags = this.normalizeTags(dto.tags);
    }
    if (dto.full_name !== undefined) {
      item.full_name = dto.full_name.trim();
    }
    if (dto.phone !== undefined) {
      item.phone = dto.phone.trim();
    }

    try {
      await item.save();
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateItemException();
      }
      throw error;
    }

    void this.contentLibraryAnalyticsService.trackEvent(userId, 'content_library_updated', item._id.toString());
    return this.toResponse(item);
  }

  async deleteItem(userId: string, itemId: string): Promise<void> {
    const item = await this.findOwnedActiveItem(userId, itemId);
    item.is_active = false;
    await item.save();
    void this.contentLibraryAnalyticsService.trackEvent(userId, 'content_library_deleted', item._id.toString());
  }

  private async queryItems(userId: string, query: ContentLibrarySearchQueryDto): Promise<ContentLibraryListDataDto> {
    const page = query.page ?? 1;
    const limit = query.limit ?? 10;
    const skip = (page - 1) * limit;
    const filter = this.buildFilter(userId, query);

    const [items, total] = await Promise.all([
      this.contentLibraryItemModel.find(filter).sort({ updatedAt: -1, createdAt: -1 }).skip(skip).limit(limit).exec(),
      this.contentLibraryItemModel.countDocuments(filter).exec(),
    ]);

    return {
      items: items.map((item) => this.toResponse(item)),
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

  private buildFilter(userId: string, query: ContentLibrarySearchQueryDto): Record<string, unknown> {
    const filter: Record<string, unknown> = {
      user_id: this.toObjectId(userId),
      is_active: true,
    };

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

  private async ensureNoDuplicate(userId: string, title: string, category: string, excludedId?: string): Promise<void> {
    const query: Record<string, unknown> = {
      user_id: this.toObjectId(userId),
      title,
      category,
      is_active: true,
    };

    if (excludedId) {
      query._id = { $ne: this.toObjectId(excludedId) };
    }

    const duplicate = await this.contentLibraryItemModel.exists(query).collation({ locale: 'en', strength: 2 });
    if (duplicate) {
      throw this.duplicateItemException();
    }
  }

  private async findOwnedActiveItem(userId: string, itemId: string): Promise<ContentLibraryItemDocument> {
    const objectId = this.toObjectId(itemId, 'CONTENT_LIBRARY_ITEM_NOT_FOUND');
    const item = await this.contentLibraryItemModel
      .findOne({
        _id: objectId,
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (!item) {
      throw new HttpException('Content library item not found', HttpStatus.NOT_FOUND, 'CONTENT_LIBRARY_ITEM_NOT_FOUND');
    }

    return item;
  }

  private duplicateItemException(): HttpException {
    return new HttpException(
      'A content library item with this title already exists in the selected category',
      HttpStatus.CONFLICT,
      'CONTENT_LIBRARY_ITEM_ALREADY_EXISTS',
      {
        title: ['A content library item with this title already exists in the selected category'],
        category: ['A content library item with this title already exists in the selected category'],
      },
    );
  }

  private toObjectId(value: string, invalidCode = 'VALIDATION_ERROR'): Types.ObjectId {
    if (!Types.ObjectId.isValid(value)) {
      if (invalidCode === 'CONTENT_LIBRARY_ITEM_NOT_FOUND') {
        throw new HttpException(
          'Content library item not found',
          HttpStatus.NOT_FOUND,
          'CONTENT_LIBRARY_ITEM_NOT_FOUND',
        );
      }

      throw new HttpException('Validation failed', HttpStatus.UNPROCESSABLE_ENTITY, invalidCode, {
        id: ['id must be a valid MongoDB ObjectId'],
      });
    }

    return new Types.ObjectId(value);
  }

  private toResponse(item: ContentLibraryItemDocument): ContentLibraryItemResponseDto {
    return {
      id: item._id.toString(),
      title: item.title,
      link: item.link,
      description: item.description,
      image: item.image_url,
      image_url: item.image_url,
      category: item.category,
      tags: item.tags,
      full_name: item.full_name,
      phone: item.phone,
      error: null,
      is_active: item.is_active,
      created_at: item.createdAt.toISOString(),
      updated_at: item.updatedAt.toISOString(),
    };
  }

  private normalizeTags(tags: string[]): string[] {
    return [...new Set(tags.map((tag) => tag.trim()).filter((tag) => tag.length > 0))];
  }

  private escapeRegex(value: string): string {
    return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }
}

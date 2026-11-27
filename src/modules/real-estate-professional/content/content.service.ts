import { HttpStatus, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { HttpException } from '../../../common/exceptions/http.exception';
import {
  CreateRealEstateContentDto,
  RealEstateContentItemResponseDto,
  RealEstateContentListDataDto,
  RealEstateContentListQueryDto,
  UpdateRealEstateContentDto,
} from './dto/content.dto';
import { RealEstateContentItem, RealEstateContentItemDocument } from './entities/content-item.schema';

@Injectable()
export class RealEstateProfessionalContentService {
  constructor(
    @InjectModel(RealEstateContentItem.name)
    private readonly contentModel: Model<RealEstateContentItem>,
  ) {}

  async listItems(query: RealEstateContentListQueryDto): Promise<RealEstateContentListDataDto> {
    this.assertValidSearch(query.search);

    const page = query.page ?? 1;
    const limit = query.limit ?? 20;
    const skip = (page - 1) * limit;
    const filter = this.buildListFilter(query);
    const sort: Record<string, 1 | -1> =
      query.sort === 'oldest' ? { createdAt: 1, _id: 1 } : { createdAt: -1, _id: -1 };

    const [records, total] = await Promise.all([
      this.contentModel.find(filter).sort(sort).skip(skip).limit(limit).exec(),
      this.contentModel.countDocuments(filter).exec(),
    ]);

    const totalPages = total === 0 ? 0 : Math.ceil(total / limit);
    const items = records.map((item) => this.toResponse(item));
    return this.toListData(items, {
      page,
      limit,
      total,
      total_pages: totalPages,
      has_next: page < totalPages,
      has_previous: page > 1 && total > 0,
    });
  }

  async createItem(userId: string, dto: CreateRealEstateContentDto): Promise<RealEstateContentItemResponseDto> {
    const title = dto.title.trim();
    await this.ensureNoDuplicateTitle(userId, title);

    try {
      const item = await this.contentModel.create({
        user_id: this.toObjectId(userId),
        title,
        description: dto.description.trim(),
        image_url: dto.image_url.trim(),
        link: dto.link?.trim() ?? null,
        city: dto.city?.trim() ?? null,
        tags: this.normalizeTags(dto.tags),
        phone: dto.phone.trim(),
        is_active: true,
      });
      return this.toResponse(await this.requirePersistedItem(item._id));
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateTitleException();
      }
      throw error;
    }
  }

  async updateItem(
    userId: string,
    itemId: string,
    dto: UpdateRealEstateContentDto,
  ): Promise<RealEstateContentItemResponseDto> {
    const item = await this.findOwnedActiveItem(userId, itemId);
    const nextTitle = dto.title?.trim() ?? item.title;
    await this.ensureNoDuplicateTitle(userId, nextTitle, item._id.toString());

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
    if (dto.city !== undefined) {
      item.city = dto.city.trim();
    }
    if (dto.tags !== undefined) {
      item.tags = this.normalizeTags(dto.tags);
    }
    if (dto.phone !== undefined) {
      item.phone = dto.phone.trim();
    }

    try {
      await item.save();
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateTitleException();
      }
      throw error;
    }

    return this.toResponse(await this.requirePersistedItem(item._id));
  }

  async deleteItem(userId: string, itemId: string): Promise<void> {
    const item = await this.findOwnedActiveItem(userId, itemId);
    item.is_active = false;
    await item.save();
  }

  private assertValidSearch(search: string | undefined): void {
    if (search === undefined) {
      return;
    }
    if (search.trim().length === 0) {
      throw new HttpException('Search term cannot be empty', HttpStatus.BAD_REQUEST, 'EMPTY_SEARCH_TERM', {
        search: ['Search term cannot be empty'],
      });
    }
  }

  private buildListFilter(query: RealEstateContentListQueryDto): Record<string, unknown> {
    const filter: Record<string, unknown> = { is_active: true };

    if (query.search?.trim()) {
      const searchRegex = new RegExp(this.escapeRegex(query.search.trim()), 'i');
      filter.$or = [{ title: searchRegex }, { description: searchRegex }, { city: searchRegex }, { tags: searchRegex }];
    }

    return filter;
  }

  private async ensureNoDuplicateTitle(userId: string, title: string, excludedId?: string): Promise<void> {
    const query: Record<string, unknown> = {
      user_id: this.toObjectId(userId),
      title,
      is_active: true,
    };
    if (excludedId) {
      query._id = { $ne: this.toObjectId(excludedId) };
    }

    const duplicate = await this.contentModel.exists(query).collation({ locale: 'en', strength: 2 });
    if (duplicate) {
      throw this.duplicateTitleException();
    }
  }

  private async findOwnedActiveItem(userId: string, itemId: string): Promise<RealEstateContentItemDocument> {
    const item = await this.contentModel
      .findOne({
        _id: this.toObjectId(itemId, 'CONTENT_NOT_FOUND'),
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (!item) {
      throw new HttpException('Content item not found', HttpStatus.NOT_FOUND, 'CONTENT_NOT_FOUND');
    }

    return item;
  }

  private async requirePersistedItem(itemId: Types.ObjectId): Promise<RealEstateContentItemDocument> {
    const item = await this.contentModel.findById(itemId).exec();
    if (!item) {
      throw new HttpException(
        'Database connection is unavailable',
        HttpStatus.SERVICE_UNAVAILABLE,
        'DATABASE_UNAVAILABLE',
      );
    }
    return item;
  }

  private duplicateTitleException(): HttpException {
    return new HttpException(
      'A content item with this name already exists',
      HttpStatus.CONFLICT,
      'CONTENT_ALREADY_EXISTS',
      { title: ['A content item with this name already exists'] },
    );
  }

  private toObjectId(value: string, invalidCode = 'VALIDATION_ERROR'): Types.ObjectId {
    if (!Types.ObjectId.isValid(value)) {
      if (invalidCode === 'CONTENT_NOT_FOUND') {
        throw new HttpException('Content item not found', HttpStatus.NOT_FOUND, 'CONTENT_NOT_FOUND');
      }
      throw new HttpException('Validation failed', HttpStatus.UNPROCESSABLE_ENTITY, invalidCode, {
        id: ['id must be a valid MongoDB ObjectId'],
      });
    }
    return new Types.ObjectId(value);
  }

  private toListData(
    items: RealEstateContentItemResponseDto[],
    pagination: RealEstateContentListDataDto['pagination'],
  ): RealEstateContentListDataDto {
    const preview = items[0];
    return {
      items,
      pagination,
      id: preview?.id ?? null,
      name: preview?.name ?? null,
      description: preview?.description ?? null,
      city: preview?.city ?? null,
      link: preview?.link ?? null,
      error: null,
    };
  }

  private toResponse(item: RealEstateContentItemDocument): RealEstateContentItemResponseDto {
    return {
      id: item._id.toString(),
      name: item.title,
      description: item.description,
      city: item.city,
      link: item.link,
      image_url: item.image_url,
      tags: item.tags,
      phone: item.phone,
      error: null,
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

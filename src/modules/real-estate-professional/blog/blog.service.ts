import { HttpStatus, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model, Types } from 'mongoose';
import { HttpException } from '../../../common/exceptions/http.exception';
import {
  BlogListDataDto,
  BlogListQueryDto,
  BlogPostDetailDto,
  BlogPostListItemDto,
  CreateBlogPostDto,
  UpdateBlogPostDto,
} from './dto/blog.dto';
import { RealEstateBlogPost, RealEstateBlogPostDocument } from './entities/blog-post.schema';

@Injectable()
export class RealEstateProfessionalBlogService {
  constructor(
    @InjectModel(RealEstateBlogPost.name)
    private readonly blogModel: Model<RealEstateBlogPost>,
  ) {}

  async listPosts(query: BlogListQueryDto): Promise<BlogListDataDto> {
    this.assertValidSearch(query.search);

    const page = query.page ?? 1;
    const limit = query.limit ?? 20;
    const skip = (page - 1) * limit;
    const filter = this.buildListFilter(query);
    const sort: Record<string, 1 | -1> =
      query.sort === 'oldest' ? { createdAt: 1, _id: 1 } : { createdAt: -1, _id: -1 };

    const [records, total] = await Promise.all([
      this.blogModel.find(filter).sort(sort).skip(skip).limit(limit).exec(),
      this.blogModel.countDocuments(filter).exec(),
    ]);

    const totalPages = total === 0 ? 0 : Math.ceil(total / limit);
    const items = records.map((post) => this.toListItem(post));

    return this.toListData(items, {
      page,
      limit,
      total,
      total_pages: totalPages,
      has_next: page < totalPages,
      has_previous: page > 1 && total > 0,
    });
  }

  async getPostById(postId: string): Promise<BlogPostDetailDto> {
    const post = await this.blogModel
      .findOne({
        _id: this.toObjectId(postId, 'BLOG_NOT_FOUND'),
        is_active: true,
      })
      .exec();

    if (!post) {
      throw new HttpException('Blog post not found', HttpStatus.NOT_FOUND, 'BLOG_NOT_FOUND');
    }

    return this.toDetail(post);
  }

  async createPost(userId: string, dto: CreateBlogPostDto): Promise<BlogPostDetailDto> {
    const title = dto.title.trim();
    await this.ensureNoDuplicateTitle(userId, title);

    try {
      const post = await this.blogModel.create({
        user_id: this.toObjectId(userId),
        title,
        author_email: dto.author_email.trim().toLowerCase(),
        content: dto.content.trim(),
        description: dto.description.trim(),
        image_url: dto.image_url.trim(),
        link: dto.link?.trim() ?? null,
        phone: dto.phone.trim(),
        terms_accepted: true,
        is_active: true,
      });
      return this.toDetail(await this.requirePersistedPost(post._id));
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateTitleException();
      }
      throw error;
    }
  }

  async updatePost(
    userId: string,
    postId: string,
    dto: UpdateBlogPostDto,
  ): Promise<BlogPostDetailDto> {
    const post = await this.findOwnedActivePost(userId, postId);
    const nextTitle = dto.title?.trim() ?? post.title;
    await this.ensureNoDuplicateTitle(userId, nextTitle, post._id.toString());

    if (dto.title !== undefined) {
      post.title = nextTitle;
    }
    if (dto.author_email !== undefined) {
      post.author_email = dto.author_email.trim().toLowerCase();
    }
    if (dto.content !== undefined) {
      post.content = dto.content.trim();
    }
    if (dto.description !== undefined) {
      post.description = dto.description.trim();
    }
    if (dto.image_url !== undefined) {
      post.image_url = dto.image_url.trim();
    }
    if (dto.link !== undefined) {
      post.link = dto.link.trim();
    }
    if (dto.phone !== undefined) {
      post.phone = dto.phone.trim();
    }

    try {
      await post.save();
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw this.duplicateTitleException();
      }
      throw error;
    }

    return this.toDetail(await this.requirePersistedPost(post._id));
  }

  async deletePost(userId: string, postId: string): Promise<void> {
    const post = await this.findOwnedActivePost(userId, postId);
    post.is_active = false;
    await post.save();
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

  private buildListFilter(query: BlogListQueryDto): Record<string, unknown> {
    const filter: Record<string, unknown> = { is_active: true };

    if (query.search?.trim()) {
      const searchRegex = new RegExp(this.escapeRegex(query.search.trim()), 'i');
      filter.$or = [{ title: searchRegex }, { description: searchRegex }, { content: searchRegex }];
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

    const duplicate = await this.blogModel.exists(query).collation({ locale: 'en', strength: 2 });
    if (duplicate) {
      throw this.duplicateTitleException();
    }
  }

  private async findOwnedActivePost(userId: string, postId: string): Promise<RealEstateBlogPostDocument> {
    const post = await this.blogModel
      .findOne({
        _id: this.toObjectId(postId, 'BLOG_NOT_FOUND'),
        user_id: this.toObjectId(userId),
        is_active: true,
      })
      .exec();

    if (!post) {
      throw new HttpException('Blog post not found', HttpStatus.NOT_FOUND, 'BLOG_NOT_FOUND');
    }

    return post;
  }

  private async requirePersistedPost(postId: Types.ObjectId): Promise<RealEstateBlogPostDocument> {
    const post = await this.blogModel.findById(postId).exec();
    if (!post) {
      throw new HttpException(
        'Database connection is unavailable',
        HttpStatus.SERVICE_UNAVAILABLE,
        'DATABASE_UNAVAILABLE',
      );
    }
    return post;
  }

  private duplicateTitleException(): HttpException {
    return new HttpException(
      'A blog post with this title already exists',
      HttpStatus.CONFLICT,
      'BLOG_ALREADY_EXISTS',
      { title: ['A blog post with this title already exists'] },
    );
  }

  private toObjectId(value: string, invalidCode = 'VALIDATION_ERROR'): Types.ObjectId {
    if (!Types.ObjectId.isValid(value)) {
      if (invalidCode === 'BLOG_NOT_FOUND') {
        throw new HttpException('Blog post not found', HttpStatus.NOT_FOUND, 'BLOG_NOT_FOUND');
      }
      throw new HttpException('Validation failed', HttpStatus.UNPROCESSABLE_ENTITY, invalidCode, {
        id: ['id must be a valid MongoDB ObjectId'],
      });
    }
    return new Types.ObjectId(value);
  }

  private toListData(
    items: BlogPostListItemDto[],
    pagination: BlogListDataDto['pagination'],
  ): BlogListDataDto {
    const preview = items[0];
    return {
      items,
      pagination,
      id: preview?.id ?? null,
      title: preview?.title ?? null,
      description: preview?.description ?? null,
      link: preview?.link ?? null,
      error: null,
    };
  }

  private toListItem(post: RealEstateBlogPostDocument): BlogPostListItemDto {
    return {
      id: post._id.toString(),
      title: post.title,
      description: post.description,
      author_email: post.author_email,
      link: post.link,
      image_url: post.image_url,
      phone: post.phone,
      error: null,
      metadata: {
        created_at: post.createdAt.toISOString(),
        updated_at: post.updatedAt.toISOString(),
      },
    };
  }

  private toDetail(post: RealEstateBlogPostDocument): BlogPostDetailDto {
    return {
      id: post._id.toString(),
      title: post.title,
      author_email: post.author_email,
      content: post.content,
      description: post.description,
      link: post.link,
      phone: post.phone,
      terms_accepted: post.terms_accepted,
      metadata: {
        created_at: post.createdAt.toISOString(),
        updated_at: post.updatedAt.toISOString(),
      },
      error: null,
    };
  }

  private escapeRegex(value: string): string {
    return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return typeof error === 'object' && error !== null && Reflect.get(error, 'code') === 11000;
  }
}
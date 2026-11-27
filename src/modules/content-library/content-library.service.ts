import { Injectable, NotFoundException, BadRequestException } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { Model } from 'mongoose';
import { ContentLibraryItem } from './entities/content-library-item.schema';
import { ContentLibraryDedicatedSearchQueryDto } from './dto/content-library-search.dto';
import { ContentLibraryListDataDto } from './dto/content-library.dto';

@Injectable()
export class ContentLibraryService {
  constructor(@InjectModel(ContentLibraryItem.name) private readonly contentLibraryItemModel: Model<ContentLibraryItem>) {}

  async searchPublicLibraryItems(query: ContentLibraryDedicatedSearchQueryDto): Promise<ContentLibraryListDataDto> {
    if (!query.query) {
      throw new BadRequestException('Search query cannot be empty');
    }

    const { page, limit, skip } = normalizePaginationQuery(
      { page: query.page, limit: query.limit },
      { defaultLimit: 20 },
    );
    const filter = this.buildPublicSearchFilter(query);

    const [items, total] = await Promise.all([
      this.contentLibraryItemModel
        .find(filter)
        .sort({ updatedAt: -1, createdAt: -1, _id: -1 })
        .skip(skip)
        .limit(limit)
        .exec(),
      this.contentLibraryItemModel.countDocuments(filter).exec(),
    ]);

    if (total === 0) {
      throw new NotFoundException('No content library items matched the search query');
    }

    const paginated = buildPaginatedResult(
      items.map((item) => this.toResponse(item)),
      total,
      page,
      limit,
    );

    return {
      items: paginated.items,
      pagination: this.toContentLibraryPagination(paginated.pagination),
    };
  }
}

import { Controller, Get, Query } from '@nestjs/common';
import { ContentLibraryService } from './content-library.service';
import { ContentLibraryDedicatedSearchQueryDto } from './dto/content-library-search.dto';

@Controller('content-library')
export class ContentLibrarySearchController {
  constructor(private readonly contentLibraryService: ContentLibraryService) {}

  @Get('search')
  async searchPublicLibraryItems(@Query() query: ContentLibraryDedicatedSearchQueryDto) {
    return {
      message: 'Content library search completed successfully',
      data: await this.contentLibraryService.searchPublicLibraryItems(query),
    };
  }
}

import { BadRequestException, Controller, Get, HttpStatus, Query, ValidationPipe } from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiInternalServerErrorResponse,
  ApiNotFoundResponse,
  ApiOkResponse,
  ApiOperation,
  ApiQuery,
  ApiTags,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { ContentLibraryService } from './content-library.service';
import { ContentLibraryDedicatedSearchQueryDto } from './dto/content-library-search.dto';
import { ContentLibraryListDataDto, ContentLibraryListResponseDto } from './dto/content-library.dto';

const searchValidationPipe = new ValidationPipe({
  whitelist: true,
  forbidNonWhitelisted: true,
  transform: true,
  errorHttpStatusCode: HttpStatus.BAD_REQUEST,
  exceptionFactory: (errors) =>
    new BadRequestException({
      message: 'Validation failed',
      errors: errors.reduce<Record<string, string[]>>((details, error) => {
        const messages = Object.values(error.constraints ?? {});
        if (messages.length > 0) {
          details[error.property] = messages;
        }
        return details;
      }, {}),
    }),
});

@ApiTags('Real Estate Professional Content Library')
@Controller('content-library')
export class ContentLibrarySearchController {
  constructor(private readonly contentLibraryService: ContentLibraryService) {}

  @Get('search')
  @ApiOperation({
    summary: 'Search content library items',
    description:
      'Searches active content library items by keywords for the Real Estate Professional Content Library screen. Public access is allowed for all users. Requires a non-empty `query` parameter. Returns paginated matches; responds with 404 when no active items match the search criteria.',
  })
  @ApiQuery({
    name: 'query',
    required: true,
    description: 'Keyword matched against title, description, category, tags, full name, and phone.',
    example: 'luxury',
  })
  @ApiQuery({
    name: 'full_name',
    required: false,
    description: 'Optional filter for the Figma #Name.40 field stored on content items.',
    example: 'Jane Doe',
  })
  @ApiQuery({
    name: 'phone',
    required: false,
    description: 'Optional filter for the phone field stored on content items.',
    example: '+1-555-0100',
  })
  @ApiQuery({ name: 'page', required: false, description: 'Results page number.', example: 1 })
  @ApiQuery({ name: 'limit', required: false, description: 'Results per page (max 100).', example: 20 })
  @ApiOkResponse({
    description: 'Content library search completed successfully.',
    type: ContentLibraryListResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Content library search completed successfully',
        data: {
          items: [
            {
              id: '66df0b7814b3e891e4ebcd21',
              title: 'Luxury Listing Social Template',
              link: 'https://example.com/content-library/luxury-listing-template',
              description:
                'Editable social post template designed for luxury property launches and premium brand campaigns.',
              image: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
              image_url: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
              category: 'Social Media',
              tags: ['luxury', 'instagram', 'listing'],
              full_name: 'Jane Doe',
              phone: '+1-555-0100',
              error: null,
              is_active: true,
              created_at: '2026-06-01T10:00:00.000Z',
              updated_at: '2026-06-02T12:30:00.000Z',
            },
          ],
          pagination: {
            page: 1,
            limit: 20,
            total: 1,
            total_pages: 1,
            has_next_page: false,
            has_previous_page: false,
          },
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'Missing, empty, or malformed search query parameters.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({
    description: 'No active content library items matched the search query.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Pagination query validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async searchContentLibrary(
    @Query(searchValidationPipe) query: ContentLibraryDedicatedSearchQueryDto,
  ): Promise<{ message: string; data: ContentLibraryListDataDto }> {
    return {
      message: 'Content library search completed successfully',
      data: await this.contentLibraryService.searchPublicLibraryItems(query),
    };
  }
}
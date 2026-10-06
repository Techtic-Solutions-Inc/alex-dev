import {
  BadRequestException,
  Body,
  Controller,
  Delete,
  Get,
  HttpCode,
  HttpStatus,
  Param,
  Post,
  Put,
  Query,
  Req,
  UseGuards,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiBearerAuth,
  ApiBody,
  ApiConflictResponse,
  ApiCreatedResponse,
  ApiForbiddenResponse,
  ApiInternalServerErrorResponse,
  ApiNoContentResponse,
  ApiNotFoundResponse,
  ApiOkResponse,
  ApiOperation,
  ApiParam,
  ApiQuery,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { AuthenticatedRequest, JwtAuthGuard } from '../../common/guards/jwt.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { Roles } from '../../common/guards/roles.decorator';
import { ContentLibraryService } from './content-library.service';
import {
  ContentLibraryCreateResponseDto,
  ContentLibraryItemResponseDto,
  ContentLibraryListDataDto,
  ContentLibraryListResponseDto,
  ContentLibrarySearchQueryDto,
  ContentLibraryUpdateResponseDto,
  CreateContentLibraryItemDto,
  UpdateContentLibraryItemDto,
} from './dto/content-library.dto';

const contentLibraryValidationPipe = new ValidationPipe({
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

@ApiTags('Content Library')
@ApiBearerAuth('access-token')
@UseGuards(JwtAuthGuard, RolesGuard)
@Roles('agent', 'admin', 'marketing_manager', 'real_estate_professional')
@Controller('content-library')
export class ContentLibraryController {
  constructor(private readonly contentLibraryService: ContentLibraryService) {}

  @Get()
  @ApiOperation({
    summary: 'List content library items',
    description:
      'Returns active content library items for the authenticated and authorized user. Supports frontend list rendering, empty-state success responses, pagination, and optional filtering by free-text query and category.',
  })
  @ApiQuery({ name: 'q', required: false, description: 'Optional free-text search term.', example: 'luxury' })
  @ApiQuery({ name: 'category', required: false, description: 'Optional category filter.', example: 'Social Media' })
  @ApiQuery({ name: 'page', required: false, description: 'Results page number.', example: 1 })
  @ApiQuery({ name: 'limit', required: false, description: 'Results per page.', example: 10 })
  @ApiOkResponse({
    description: 'Content library items retrieved successfully.',
    type: ContentLibraryListResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Content library items retrieved successfully',
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
            limit: 10,
            total: 1,
            total_pages: 1,
            has_next_page: false,
            has_previous_page: false,
          },
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Malformed query parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have a role permitted to access the content library.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Content library resource not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Content library request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async listItems(
    @Req() request: AuthenticatedRequest,
    @Query(contentLibraryValidationPipe) query: ContentLibrarySearchQueryDto,
  ): Promise<{ message: string; data: ContentLibraryListDataDto }> {
    return {
      message: 'Content library items retrieved successfully',
      data: await this.contentLibraryService.listItems(request.user.sub, query),
    };
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Create a content library item',
    description:
      'Creates a new active content library item for the authenticated and authorized user. The typed JSON request body is fully documented for Swagger and includes all Figma-backed fields such as full_name and phone.',
  })
  @ApiBody({ type: CreateContentLibraryItemDto, description: 'New content library item payload.' })
  @ApiCreatedResponse({
    description: 'Content library item created successfully.',
    type: ContentLibraryCreateResponseDto,
  })
  @ApiBadRequestResponse({
    description: 'Required fields are missing or invalid, including malformed URLs or phone values.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have permission to create content library items.',
    type: ApiErrorResponseDto,
  })
  @ApiConflictResponse({
    description: 'An active content item with the same title already exists in the selected category.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Content library resource not found.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async createItem(
    @Req() request: AuthenticatedRequest,
    @Body(contentLibraryValidationPipe) dto: CreateContentLibraryItemDto,
  ): Promise<{ message: string; data: ContentLibraryItemResponseDto }> {
    return {
      message: 'Content library item created successfully',
      data: await this.contentLibraryService.createItem(request.user.sub, dto),
    };
  }

  @Get('search')
  @ApiOperation({
    summary: 'Search content library items',
    description:
      'Searches active content library items for the authenticated and authorized user. This endpoint is optimized for the frontend search box and returns the same response shape as the main list endpoint.',
  })
  @ApiOkResponse({
    description: 'Content library search completed successfully.',
    type: ContentLibraryListResponseDto,
  })
  @ApiBadRequestResponse({ description: 'Malformed search query parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have permission to search the content library.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Content library resource not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Content library request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async searchItems(
    @Req() request: AuthenticatedRequest,
    @Query(contentLibraryValidationPipe) query: ContentLibrarySearchQueryDto,
  ): Promise<{ message: string; data: ContentLibraryListDataDto }> {
    return {
      message: 'Content library search completed successfully',
      data: await this.contentLibraryService.searchItems(request.user.sub, query),
    };
  }

  @Get(':id')
  @ApiOperation({
    summary: 'Get content library item details',
    description:
      'Returns the full details for a single active content library item owned by the authenticated and authorized user. This payload includes all fields required by the frontend detail screen.',
  })
  @ApiParam({
    name: 'id',
    description: 'MongoDB ObjectId of the content library item.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @ApiOkResponse({
    description: 'Content library item retrieved successfully.',
    type: ContentLibraryUpdateResponseDto,
  })
  @ApiBadRequestResponse({ description: 'Malformed request parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have permission to access this content library item.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Content library item was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Content library request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async getItem(
    @Req() request: AuthenticatedRequest,
    @Param('id') id: string,
  ): Promise<{ message: string; data: ContentLibraryItemResponseDto }> {
    return {
      message: 'Content library item retrieved successfully',
      data: await this.contentLibraryService.getItem(request.user.sub, id),
    };
  }

  @Put(':id')
  @ApiOperation({
    summary: 'Update a content library item',
    description:
      'Updates an existing active content library item owned by the authenticated and authorized user. The request body remains fully typed for Swagger and supports partial updates across all editable fields.',
  })
  @ApiParam({
    name: 'id',
    description: 'MongoDB ObjectId of the content library item.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @ApiBody({ type: UpdateContentLibraryItemDto, description: 'Partial content library item update payload.' })
  @ApiOkResponse({
    description: 'Content library item updated successfully.',
    type: ContentLibraryUpdateResponseDto,
  })
  @ApiBadRequestResponse({ description: 'Malformed request payload.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have permission to update content library items.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Content library item was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'An active content item with the same title already exists in the selected category.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async updateItem(
    @Req() request: AuthenticatedRequest,
    @Param('id') id: string,
    @Body(contentLibraryValidationPipe) dto: UpdateContentLibraryItemDto,
  ): Promise<{ message: string; data: ContentLibraryItemResponseDto }> {
    return {
      message: 'Content library item updated successfully',
      data: await this.contentLibraryService.updateItem(request.user.sub, id, dto),
    };
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({
    summary: 'Delete a content library item',
    description:
      'Soft-deletes an active content library item owned by the authenticated and authorized user by marking it inactive. The endpoint returns no response body on success.',
  })
  @ApiParam({
    name: 'id',
    description: 'MongoDB ObjectId of the content library item.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @ApiNoContentResponse({ description: 'Content library item deleted successfully.' })
  @ApiBadRequestResponse({ description: 'Malformed request parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'Authenticated user does not have permission to delete content library items.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Content library item was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Content library request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async deleteItem(@Req() request: AuthenticatedRequest, @Param('id') id: string): Promise<void> {
    await this.contentLibraryService.deleteItem(request.user.sub, id);
  }
}

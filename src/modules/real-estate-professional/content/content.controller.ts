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
import { ApiErrorResponseDto } from '../../../common/dto/api-response.dto';
import { AuthenticatedRequest, JwtAuthGuard } from '../../../common/guards/jwt.guard';
import { Roles } from '../../../common/guards/roles.decorator';
import { RolesGuard } from '../../../common/guards/roles.guard';
import { RealEstateProfessionalContentService } from './content.service';
import {
  CreateRealEstateContentDto,
  RealEstateContentItemResponseDto,
  RealEstateContentListDataDto,
  RealEstateContentListQueryDto,
  UpdateRealEstateContentDto,
} from './dto/content.dto';

const contentValidationPipe = new ValidationPipe({
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

@ApiTags('Real Estate Professional Content')
@Controller('real-estate-professional/content')
export class RealEstateProfessionalContentController {
  constructor(private readonly contentService: RealEstateProfessionalContentService) {}

  @Get()
  @ApiOperation({
    summary: 'List content items',
    description:
      'Returns paginated active content templates for the Content List screen. Public access is allowed. Supports `search`, `sort` (`newest`|`oldest`), `page`, and `limit` query parameters.',
  })
  @ApiQuery({ name: 'search', required: false, description: 'Optional search term. Empty values return 400.', example: 'instagram' })
  @ApiQuery({ name: 'sort', required: false, enum: ['newest', 'oldest'], example: 'newest' })
  @ApiQuery({ name: 'page', required: false, example: 1 })
  @ApiQuery({ name: 'limit', required: false, example: 20 })
  @ApiOkResponse({
    description: 'Content items retrieved successfully.',
    schema: {
      example: {
        success: true,
        message: 'Content items retrieved successfully',
        data: {
          items: [
            {
              id: '66df0b7814b3e891e4ebcd21',
              name: 'Hates to see me coming',
              description: 'Trend-ready Instagram caption.',
              city: 'Austin',
              link: 'https://example.com/templates/hates-to-see-me-coming',
              image_url: 'https://cdn.example.com/templates/hates-to-see-me-coming.jpg',
              tags: ['instagram', 'reel'],
              phone: '+1-555-0100',
              error: null,
              created_at: '2026-06-01T10:00:00.000Z',
              updated_at: '2026-06-02T12:30:00.000Z',
            },
          ],
          pagination: {
            page: 1,
            limit: 20,
            total: 1,
            total_pages: 1,
            has_next: false,
            has_previous: false,
          },
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Empty search term or invalid query parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Unauthorized.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async listItems(
    @Query(contentValidationPipe) query: RealEstateContentListQueryDto,
  ): Promise<{ message: string; data: RealEstateContentListDataDto }> {
    return {
      message: 'Content items retrieved successfully',
      data: await this.contentService.listItems(query),
    };
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('real_estate_professional', 'admin', 'agent', 'marketing_manager')
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Create a content item',
    description:
      'Creates a content template for the authenticated Real Estate Professional. Requires `terms_accepted=true` and rejects duplicate content names for the same user.',
  })
  @ApiBody({ type: CreateRealEstateContentDto })
  @ApiCreatedResponse({ description: 'Content item created successfully.' })
  @ApiBadRequestResponse({
    description: 'Validation failed, including missing or false `terms_accepted`.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'User role cannot create content.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Duplicate content name.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Not found.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async createItem(
    @Req() request: AuthenticatedRequest,
    @Body(contentValidationPipe) dto: CreateRealEstateContentDto,
  ): Promise<{ message: string; data: RealEstateContentItemResponseDto }> {
    return {
      message: 'Content item created successfully',
      data: await this.contentService.createItem(request.user.sub, dto),
    };
  }

  @Put(':id')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('real_estate_professional', 'admin', 'agent', 'marketing_manager')
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Update a content item',
    description: 'Updates an owned active content item for the authenticated user.',
  })
  @ApiParam({ name: 'id', description: 'MongoDB ObjectId of the content item.' })
  @ApiBody({ type: UpdateRealEstateContentDto })
  @ApiOkResponse({ description: 'Content item updated successfully.' })
  @ApiBadRequestResponse({ description: 'Invalid request payload.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'User role cannot update content.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Content item not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Duplicate content name.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async updateItem(
    @Req() request: AuthenticatedRequest,
    @Param('id') id: string,
    @Body(contentValidationPipe) dto: UpdateRealEstateContentDto,
  ): Promise<{ message: string; data: RealEstateContentItemResponseDto }> {
    return {
      message: 'Content item updated successfully',
      data: await this.contentService.updateItem(request.user.sub, id, dto),
    };
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('real_estate_professional', 'admin', 'agent', 'marketing_manager')
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Delete a content item',
    description: 'Soft-deletes an owned content item. Returns 204 with no response body.',
  })
  @ApiParam({ name: 'id', description: 'MongoDB ObjectId of the content item.' })
  @ApiNoContentResponse({ description: 'Content item deleted successfully.' })
  @ApiBadRequestResponse({ description: 'Invalid id.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'User role cannot delete content.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Content item not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async deleteItem(@Req() request: AuthenticatedRequest, @Param('id') id: string): Promise<void> {
    await this.contentService.deleteItem(request.user.sub, id);
  }
}
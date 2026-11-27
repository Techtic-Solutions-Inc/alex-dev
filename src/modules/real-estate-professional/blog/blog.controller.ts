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
import { BlogDetailAccessGuard } from './blog-detail.guard';
import { RealEstateProfessionalBlogService } from './blog.service';
import {
  BlogListDataDto,
  BlogListQueryDto,
  BlogPostDetailDto,
  CreateBlogPostDto,
  UpdateBlogPostDto,
} from './dto/blog.dto';

const blogValidationPipe = new ValidationPipe({
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

@ApiTags('Real Estate Professional Blog')
@Controller('real-estate-professional/blog')
export class RealEstateProfessionalBlogController {
  constructor(private readonly blogService: RealEstateProfessionalBlogService) {}

  @Get()
  @ApiOperation({
    summary: 'List blog posts',
    description:
      'Returns paginated active blog posts for the Blog screen. Public access is allowed. Supports `search`, `sort` (`newest`|`oldest`), `page`, and `limit` query parameters.',
  })
  @ApiQuery({ name: 'search', required: false, example: 'market' })
  @ApiQuery({ name: 'sort', required: false, enum: ['newest', 'oldest'], example: 'newest' })
  @ApiQuery({ name: 'page', required: false, example: 1 })
  @ApiQuery({ name: 'limit', required: false, example: 20 })
  @ApiOkResponse({
    description: 'Blog posts retrieved successfully.',
    schema: {
      example: {
        success: true,
        message: 'Blog posts retrieved successfully',
        data: {
          items: [
            {
              id: '66df0b7814b3e891e4ebcd21',
              title: 'Hates to see me coming',
              description: 'Insights on local market positioning.',
              author_email: 'hello@agentwisemarketing.com',
              link: 'https://example.com/blog/hates-to-see-me-coming',
              image_url: 'https://cdn.example.com/blog/hates-to-see-me-coming.jpg',
              phone: '+1-555-0100',
              error: null,
              metadata: {
                created_at: '2026-01-01T00:00:00.000Z',
                updated_at: '2026-01-01T00:00:00.000Z',
              },
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
          id: '66df0b7814b3e891e4ebcd21',
          title: 'Hates to see me coming',
          description: 'Insights on local market positioning.',
          link: 'https://example.com/blog/hates-to-see-me-coming',
          error: null,
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Invalid query parameters.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async listPosts(
    @Query(blogValidationPipe) query: BlogListQueryDto,
  ): Promise<{ message: string; data: BlogListDataDto }> {
    return {
      message: 'Blog posts retrieved successfully',
      data: await this.blogService.listPosts(query),
    };
  }

  @Get(':id')
  @UseGuards(BlogDetailAccessGuard, RolesGuard)
  @Roles('real_estate_professional', 'admin', 'agent', 'marketing_manager')
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Retrieve blog details by ID',
    description:
      'Returns full blog content and author metadata for the Blog Details screen. Requires authentication; anonymous callers receive 403.',
  })
  @ApiParam({ name: 'id', description: 'MongoDB ObjectId of the blog post.' })
  @ApiOkResponse({
    description: 'Blog post retrieved successfully.',
    schema: {
      example: {
        success: true,
        message: 'Blog post retrieved successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          title: 'Hates to see me coming',
          author_email: 'hello@agentwisemarketing.com',
          content: 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.',
          description: 'Insights on local market positioning.',
          link: 'https://example.com/blog/hates-to-see-me-coming',
          phone: '+1-555-0100',
          terms_accepted: true,
          metadata: {
            created_at: '2026-01-01T00:00:00.000Z',
            updated_at: '2026-01-01T00:00:00.000Z',
          },
          error: null,
        },
      },
    },
  })
  @ApiForbiddenResponse({
    description: 'Missing or invalid credentials, or insufficient role.',
    type: ApiErrorResponseDto,
  })
  @ApiNotFoundResponse({ description: 'Blog post not found.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Unauthorized.', type: ApiErrorResponseDto })
  @ApiBadRequestResponse({ description: 'Invalid id.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async getPostById(@Param('id') id: string): Promise<{ message: string; data: BlogPostDetailDto }> {
    return {
      message: 'Blog post retrieved successfully',
      data: await this.blogService.getPostById(id),
    };
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('real_estate_professional', 'admin', 'agent', 'marketing_manager')
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Create a blog post',
    description:
      'Creates a blog post for the authenticated user. Requires `terms_accepted=true` and rejects duplicate titles.',
  })
  @ApiBody({ type: CreateBlogPostDto })
  @ApiCreatedResponse({ description: 'Blog post created successfully.' })
  @ApiBadRequestResponse({
    description: 'Validation failed, including empty title or missing `terms_accepted`.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'User role cannot create blog posts.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Duplicate blog title.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async createPost(
    @Req() request: AuthenticatedRequest,
    @Body(blogValidationPipe) dto: CreateBlogPostDto,
  ): Promise<{ message: string; data: BlogPostDetailDto }> {
    return {
      message: 'Blog post created successfully',
      data: await this.blogService.createPost(request.user.sub, dto),
    };
  }

  @Put(':id')
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('real_estate_professional', 'admin', 'agent', 'marketing_manager')
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Update a blog post',
    description: 'Updates an owned active blog post for the authenticated user.',
  })
  @ApiParam({ name: 'id', description: 'MongoDB ObjectId of the blog post.' })
  @ApiBody({ type: UpdateBlogPostDto })
  @ApiOkResponse({ description: 'Blog post updated successfully.' })
  @ApiBadRequestResponse({ description: 'Invalid request payload.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'User role cannot update blog posts.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Blog post not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Duplicate blog title.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async updatePost(
    @Req() request: AuthenticatedRequest,
    @Param('id') id: string,
    @Body(blogValidationPipe) dto: UpdateBlogPostDto,
  ): Promise<{ message: string; data: BlogPostDetailDto }> {
    return {
      message: 'Blog post updated successfully',
      data: await this.blogService.updatePost(request.user.sub, id, dto),
    };
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @UseGuards(JwtAuthGuard, RolesGuard)
  @Roles('real_estate_professional', 'admin', 'agent', 'marketing_manager')
  @ApiBearerAuth('access-token')
  @ApiOperation({
    summary: 'Delete a blog post',
    description: 'Soft-deletes an owned blog post. Returns 204 with no response body.',
  })
  @ApiParam({ name: 'id', description: 'MongoDB ObjectId of the blog post.' })
  @ApiNoContentResponse({ description: 'Blog post deleted successfully.' })
  @ApiBadRequestResponse({ description: 'Invalid id.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'User role cannot delete blog posts.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Blog post not found.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async deletePost(@Req() request: AuthenticatedRequest, @Param('id') id: string): Promise<void> {
    await this.blogService.deletePost(request.user.sub, id);
  }
}
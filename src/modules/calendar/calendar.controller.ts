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
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { AuthenticatedRequest, JwtAuthGuard } from '../../common/guards/jwt.guard';
import { CalendarService } from './calendar.service';
import {
  ContentCalendarCreateResponseDto,
  ContentCalendarEntryResponseDto,
  ContentCalendarListResponseDto,
  ContentCalendarUpdateResponseDto,
  CreateContentCalendarEntryDto,
  UpdateContentCalendarEntryDto,
} from './dto/content-calendar.dto';

const contentCalendarCreateValidationPipe = new ValidationPipe({
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

@ApiTags('Content Calendar')
@ApiBearerAuth('access-token')
@UseGuards(JwtAuthGuard)
@Controller('content-calendar')
export class CalendarController {
  constructor(private readonly calendarService: CalendarService) {}

  @Get()
  @ApiOperation({
    summary: 'List active content calendar entries',
    description:
      'Returns all active content calendar entries belonging to the authenticated user, sorted by scheduled date. Soft-deleted entries are excluded.',
  })
  @ApiOkResponse({
    description: 'Active content calendar entries were retrieved successfully.',
    type: ContentCalendarListResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Content calendar entries retrieved successfully',
        data: {
          items: [
            {
              id: '66df0b7814b3e891e4ebcd21',
              title: 'Market update - Austin Q2',
              date: '2026-06-15T00:00:00.000Z',
              content: 'Your personal content calendar designed to grow your business - made specifically for you.',
              description: 'Your personal content calendar designed to grow your business - made specifically for you.',
              full_name: 'Jane Doe',
              phone: '+1-555-0100',
              link: 'https://example.com/posts/austin-q2-market-update',
              error: null,
              is_active: true,
              created_at: '2026-06-01T10:00:00.000Z',
              updated_at: '2026-06-01T10:00:00.000Z',
            },
          ],
        },
      },
    },
  })
  @ApiUnauthorizedResponse({
    description: 'Missing or invalid bearer token.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async listEntries(
    @Req() request: AuthenticatedRequest,
  ): Promise<{ message: string; data: { items: ContentCalendarEntryResponseDto[] } }> {
    const items = await this.calendarService.listActiveEntries(request.user.sub);
    return {
      message: 'Content calendar entries retrieved successfully',
      data: { items },
    };
  }

  @Post()
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Create a content calendar entry',
    description:
      'Creates a new active content calendar entry for the authenticated user. Title must be unique per scheduled date. All Figma form fields (full_name, phone) are required.',
  })
  @ApiBody({
    type: CreateContentCalendarEntryDto,
    description: 'Content calendar entry payload including title, date, content, full_name, and phone.',
  })
  @ApiCreatedResponse({
    description: 'Content calendar entry was created successfully.',
    type: ContentCalendarCreateResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Content entry created successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          title: 'Market update - Austin Q2',
          date: '2026-06-15T00:00:00.000Z',
          content: 'Your personal content calendar designed to grow your business - made specifically for you.',
          description: 'Your personal content calendar designed to grow your business - made specifically for you.',
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
          link: null,
          error: null,
          is_active: true,
          created_at: '2026-06-01T10:00:00.000Z',
          updated_at: '2026-06-01T10:00:00.000Z',
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'Required fields are missing or invalid (e.g., title, date, content, full_name, phone).',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'Missing or invalid bearer token.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'An active entry with the same title already exists on the selected date.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async createEntry(
    @Req() request: AuthenticatedRequest,
    @Body(contentCalendarCreateValidationPipe) dto: CreateContentCalendarEntryDto,
  ): Promise<{ message: string; data: ContentCalendarEntryResponseDto }> {
    const entry = await this.calendarService.createEntry(request.user.sub, dto);
    return {
      message: 'Content entry created successfully',
      data: entry,
    };
  }

  @Put(':id')
  @ApiOperation({
    summary: 'Update a content calendar entry',
    description:
      'Updates an existing active content calendar entry owned by the authenticated user. At least one field must be supplied.',
  })
  @ApiParam({
    name: 'id',
    description: 'MongoDB ObjectId of the content calendar entry.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @ApiBody({
    type: UpdateContentCalendarEntryDto,
    description: 'Partial content calendar entry payload.',
  })
  @ApiOkResponse({
    description: 'Content calendar entry was updated successfully.',
    type: ContentCalendarUpdateResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Content entry updated successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          title: 'Market update - Austin Q2 revised',
          date: '2026-06-16T17:00:00.000Z',
          content: 'Updated content strategy tailored for Austin listings.',
          description: 'Updated content strategy tailored for Austin listings.',
          full_name: 'Jane Doe',
          phone: '+1-555-0101',
          link: 'https://example.com/posts/austin-q2-market-update-revised',
          error: null,
          is_active: true,
          created_at: '2026-06-01T10:00:00.000Z',
          updated_at: '2026-06-02T12:30:00.000Z',
        },
      },
    },
  })
  @ApiBadRequestResponse({ description: 'Malformed request payload.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({
    description: 'Missing or invalid bearer token.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({
    description: 'Content entry was not found or is inactive.',
    type: ApiErrorResponseDto,
  })
  @ApiConflictResponse({
    description: 'An active entry with the same title already exists on the selected date.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async updateEntry(
    @Req() request: AuthenticatedRequest,
    @Param('id') id: string,
    @Body() dto: UpdateContentCalendarEntryDto,
  ): Promise<{ message: string; data: ContentCalendarEntryResponseDto }> {
    const entry = await this.calendarService.updateEntry(request.user.sub, id, dto);
    return {
      message: 'Content entry updated successfully',
      data: entry,
    };
  }

  @Delete(':id')
  @HttpCode(HttpStatus.NO_CONTENT)
  @ApiOperation({
    summary: 'Delete a content calendar entry',
    description:
      'Soft-deletes a content calendar entry owned by the authenticated user by marking it inactive. Returns no response body.',
  })
  @ApiParam({
    name: 'id',
    description: 'MongoDB ObjectId of the content calendar entry.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @ApiNoContentResponse({ description: 'Content calendar entry was deleted successfully.' })
  @ApiUnauthorizedResponse({
    description: 'Missing or invalid bearer token.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({
    description: 'Content entry was not found or is already inactive.',
    type: ApiErrorResponseDto,
  })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async deleteEntry(@Req() request: AuthenticatedRequest, @Param('id') id: string): Promise<void> {
    await this.calendarService.deleteEntry(request.user.sub, id);
  }
}

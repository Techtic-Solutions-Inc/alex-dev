import {
  BadRequestException,
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Post,
  Query,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiBody,
  ApiConflictResponse,
  ApiCreatedResponse,
  ApiForbiddenResponse,
  ApiInternalServerErrorResponse,
  ApiNotFoundResponse,
  ApiOkResponse,
  ApiOperation,
  ApiQuery,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import {
  VisitorHomeLeadResponseDto,
  VisitorHomeSearchDataDto,
  VisitorHomeSearchQueryDto,
  VisitorHomeSearchResponseDto,
  VisitorHomeSubscribeDto,
  VisitorHomeSubscribeResponseDto,
  VisitorHomeTermsAcceptanceDto,
  VisitorHomeTermsAcceptanceResponseDto,
} from './dto/visitor-home.dto';
import { VisitorHomeService } from './visitor-home.service';
import { VisitorHomeAliasPipe } from './visitor-home-alias.pipe';

const visitorHomeValidationPipe = new ValidationPipe({
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

@ApiTags('Visitor Home')
@Controller('visitor/home')
export class VisitorHomeController {
  constructor(private readonly visitorHomeService: VisitorHomeService) {}

  /**
   * Searches public marketing content for the visitor Home screen.
   */
  @Get('search')
  @ApiOperation({
    summary: 'Search visitor Home content',
    description:
      'Public endpoint that searches active marketing content shown on the visitor Home screen. Supports free-text search, optional category filtering, pagination, and empty-state success responses. No bearer token is required.',
  })
  @ApiQuery({ name: 'q', required: false, description: 'Optional free-text search term.', example: 'templates' })
  @ApiQuery({ name: 'category', required: false, description: 'Optional category filter.', example: 'Social Media' })
  @ApiQuery({ name: 'page', required: false, description: 'Results page number.', example: 1 })
  @ApiQuery({ name: 'limit', required: false, description: 'Results per page.', example: 10 })
  @ApiOkResponse({
    description: 'Visitor home search completed successfully.',
    type: VisitorHomeSearchResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Visitor home search completed successfully',
        data: {
          items: [
            {
              id: '66df0b7814b3e891e4ebcd21',
              name: 'Luxury Listing Social Template',
              title: 'Luxury Listing Social Template',
              description: 'Help real estate professionals create content faster with ready-made templates.',
              link: 'https://example.com/visitor/home/luxury-listing-template',
              image: 'https://cdn.example.com/visitor/home/luxury-listing-template.jpg',
              image_url: 'https://cdn.example.com/visitor/home/luxury-listing-template.jpg',
              category: 'Social Media',
              tags: ['templates', 'instagram', 'listing'],
              full_name: null,
              first_name: null,
              last_name: null,
              email: null,
              phone: null,
              phone_number: null,
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
  @ApiBadRequestResponse({ description: 'Malformed search query parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({
    description: 'No authentication is required for this endpoint.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Visitor home resource was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Visitor home request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async search(
    @Query(visitorHomeValidationPipe) query: VisitorHomeSearchQueryDto,
  ): Promise<{ message: string; data: VisitorHomeSearchDataDto }> {
    return {
      message: 'Visitor home search completed successfully',
      data: await this.visitorHomeService.searchContent(query),
    };
  }

  /**
   * Submits a visitor email for marketing after terms acceptance.
   */
  @Post('subscribe')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Subscribe a visitor for marketing email',
    description:
      'Public endpoint that stores a visitor marketing lead from the Home screen. The request must include a valid email and terms_accepted=true. Figma fields full_name, email, phone, and terms_accepted are accepted, along with frontend aliases first_name, last_name, and phone_number. Duplicate subscribed emails return 409. No bearer token is required.',
  })
  @ApiBody({
    type: VisitorHomeSubscribeDto,
    description: 'Home screen subscription payload including Figma and frontend form fields.',
  })
  @ApiCreatedResponse({
    description: 'Visitor subscribed successfully.',
    type: VisitorHomeSubscribeResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Subscribed successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          name: 'Jane Doe',
          full_name: 'Jane Doe',
          first_name: 'Jane',
          last_name: 'Doe',
          email: 'jane.doe@example.com',
          phone: '+1-555-0100',
          phone_number: '+1-555-0100',
          link: null,
          description: null,
          terms_accepted: true,
          subscribed: true,
          error: null,
          created_at: '2026-06-01T10:00:00.000Z',
          updated_at: '2026-06-01T10:00:00.000Z',
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'A required field is missing, invalid, or terms were not accepted.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'No authentication is required for this endpoint.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Visitor home resource was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'The submitted email is already subscribed.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async subscribe(
    @Body(new VisitorHomeAliasPipe(), visitorHomeValidationPipe) dto: VisitorHomeSubscribeDto,
  ): Promise<{ message: string; data: VisitorHomeLeadResponseDto }> {
    return {
      message: 'Subscribed successfully',
      data: await this.visitorHomeService.subscribe(dto),
    };
  }

  /**
   * Records Privacy Policy and Terms of Service acceptance for a visitor.
   */
  @Post('terms-acceptance')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Accept terms and privacy policy',
    description:
      'Public endpoint that records Privacy Policy and Terms of Service acceptance from the visitor Home screen. The request must include a valid email and terms_accepted=true. Repeat submissions for the same email are idempotent and still return 201. No bearer token is required.',
  })
  @ApiBody({
    type: VisitorHomeTermsAcceptanceDto,
    description: 'Home screen terms-acceptance payload including Figma and frontend form fields.',
  })
  @ApiCreatedResponse({
    description: 'Terms and privacy policy accepted successfully.',
    type: VisitorHomeTermsAcceptanceResponseDto,
    schema: {
      example: {
        success: true,
        message: 'Terms and privacy policy accepted successfully',
        data: {
          id: '66df0b7814b3e891e4ebcd21',
          name: 'Jane Doe',
          full_name: 'Jane Doe',
          first_name: 'Jane',
          last_name: 'Doe',
          email: 'jane.doe@example.com',
          phone: '+1-555-0100',
          phone_number: '+1-555-0100',
          link: null,
          description: null,
          terms_accepted: true,
          subscribed: false,
          error: null,
          created_at: '2026-06-01T10:00:00.000Z',
          updated_at: '2026-06-01T10:00:00.000Z',
        },
      },
    },
  })
  @ApiBadRequestResponse({
    description: 'A required field is missing, invalid, or terms were not accepted.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({
    description: 'No authentication is required for this endpoint.',
    type: ApiErrorResponseDto,
  })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({ description: 'Visitor home resource was not found.', type: ApiErrorResponseDto })
  @ApiConflictResponse({ description: 'Visitor home request conflict.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async acceptTerms(
    @Body(new VisitorHomeAliasPipe(), visitorHomeValidationPipe) dto: VisitorHomeTermsAcceptanceDto,
  ): Promise<{ message: string; data: VisitorHomeLeadResponseDto }> {
    return {
      message: 'Terms and privacy policy accepted successfully',
      data: await this.visitorHomeService.acceptTerms(dto),
    };
  }
}

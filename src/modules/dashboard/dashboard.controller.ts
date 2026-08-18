import {
  BadRequestException,
  Body,
  Controller,
  Get,
  HttpCode,
  HttpStatus,
  Post,
  Req,
  UseGuards,
  ValidationPipe,
} from '@nestjs/common';
import {
  ApiBadRequestResponse,
  ApiBearerAuth,
  ApiConflictResponse,
  ApiCreatedResponse,
  ApiForbiddenResponse,
  ApiInternalServerErrorResponse,
  ApiNotFoundResponse,
  ApiOkResponse,
  ApiOperation,
  ApiTags,
  ApiUnauthorizedResponse,
  ApiUnprocessableEntityResponse,
} from '@nestjs/swagger';
import { ApiErrorResponseDto } from '../../common/dto/api-response.dto';
import { AuthenticatedRequest, JwtAuthGuard } from '../../common/guards/jwt.guard';
import {
  AskDashboardQuestionDto,
  CreateAnnouncementDto,
  DashboardAnalyticsEnvelopeResponseDto,
  DashboardAnnouncementCreateResponseDto,
  DashboardAnnouncementListResponseDto,
  DashboardOverviewResponseDto,
  DashboardQuestionResponseDto,
} from './dto/dashboard.dto';
import { DashboardService } from './dashboard.service';

const dashboardValidationPipe = new ValidationPipe({
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

@ApiTags('Dashboard')
@ApiBearerAuth('access-token')
@UseGuards(JwtAuthGuard)
@Controller('dashboard')
export class DashboardController {
  constructor(private readonly dashboardService: DashboardService) {}

  @Get()
  @ApiOperation({
    summary: 'Retrieve the authenticated user dashboard overview',
    description:
      'Returns the main dashboard payload for the authenticated user, including profile details, announcements, content calendar entries, and analytics/AI credit metrics required by the frontend dashboard screen.',
  })
  @ApiOkResponse({
    description: 'Dashboard overview retrieved successfully.',
    type: DashboardOverviewResponseDto,
  })
  @ApiBadRequestResponse({ description: 'Malformed request parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiNotFoundResponse({
    description: 'No dashboard data is available for the authenticated user.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async getOverview(@Req() request: AuthenticatedRequest) {
    return {
      message: 'Dashboard overview retrieved successfully',
      data: await this.dashboardService.getOverview(request.user.sub),
    };
  }

  @Get('announcements')
  @ApiOperation({
    summary: 'List dashboard announcements',
    description:
      'Returns the dashboard announcements belonging to the authenticated user in reverse chronological order. Response fields include frontend contract fields such as id, title, description, link, status, and error.',
  })
  @ApiOkResponse({
    description: 'Announcements retrieved successfully.',
    type: DashboardAnnouncementListResponseDto,
  })
  @ApiBadRequestResponse({ description: 'Malformed request parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async listAnnouncements(@Req() request: AuthenticatedRequest) {
    const items = await this.dashboardService.listAnnouncements(request.user.sub);
    return {
      message: 'Announcements retrieved successfully',
      data: {
        items,
        total: items.length,
      },
    };
  }

  @Post('announcements')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Create a dashboard announcement',
    description:
      'Creates a new announcement for the authenticated user. The JSON request body is fully typed for Swagger and must include the Figma fields full_name, email, and phone in addition to the announcement title and content.',
  })
  @ApiCreatedResponse({
    description: 'Announcement created successfully.',
    type: DashboardAnnouncementCreateResponseDto,
  })
  @ApiBadRequestResponse({
    description: 'Required fields are missing or invalid, including invalid email or phone values.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiConflictResponse({
    description: 'An announcement with the same title already exists for the authenticated user.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async createAnnouncement(
    @Req() request: AuthenticatedRequest,
    @Body(dashboardValidationPipe) dto: CreateAnnouncementDto,
  ) {
    return {
      message: 'Announcement created successfully',
      data: await this.dashboardService.createAnnouncement(request.user.sub, dto),
    };
  }

  @Get('analytics')
  @ApiOperation({
    summary: 'Retrieve dashboard analytics',
    description:
      'Returns analytics and AI credit information for the authenticated user, including content_generated, downloads, current credit usage, total credits, and remaining credits.',
  })
  @ApiOkResponse({
    description: 'Dashboard analytics retrieved successfully.',
    type: DashboardAnalyticsEnvelopeResponseDto,
  })
  @ApiBadRequestResponse({ description: 'Malformed request parameters.', type: ApiErrorResponseDto })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({ description: 'Request is forbidden.', type: ApiErrorResponseDto })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async getAnalytics(@Req() request: AuthenticatedRequest) {
    return {
      message: 'Dashboard analytics retrieved successfully',
      data: await this.dashboardService.getAnalytics(request.user.sub),
    };
  }

  @Post('questions')
  @HttpCode(HttpStatus.CREATED)
  @ApiOperation({
    summary: 'Ask the dashboard AI assistant a question',
    description:
      'Consumes one AI credit and returns a generated response for the authenticated user. Users with AI generation disabled receive 403, and users with no remaining credits receive 409.',
  })
  @ApiCreatedResponse({
    description: 'Question answered successfully and AI credits were updated.',
    type: DashboardQuestionResponseDto,
  })
  @ApiBadRequestResponse({
    description: 'The submitted question is empty, too long, or otherwise invalid.',
    type: ApiErrorResponseDto,
  })
  @ApiUnauthorizedResponse({ description: 'Missing or invalid bearer token.', type: ApiErrorResponseDto })
  @ApiForbiddenResponse({
    description: 'The authenticated user is not allowed to use AI content generation features.',
    type: ApiErrorResponseDto,
  })
  @ApiConflictResponse({
    description: 'The authenticated user has exhausted their AI credit limit.',
    type: ApiErrorResponseDto,
  })
  @ApiUnprocessableEntityResponse({ description: 'Request validation failed.', type: ApiErrorResponseDto })
  @ApiInternalServerErrorResponse({ description: 'Unexpected server error.', type: ApiErrorResponseDto })
  async askQuestion(@Req() request: AuthenticatedRequest, @Body(dashboardValidationPipe) dto: AskDashboardQuestionDto) {
    return {
      message: 'Question answered successfully',
      data: await this.dashboardService.askQuestion(request.user.sub, dto),
    };
  }
}

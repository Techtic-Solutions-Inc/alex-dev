import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { IsEmail, IsNotEmpty, IsOptional, IsString, IsUrl, Matches, MaxLength } from 'class-validator';
import { ContentCalendarEntryResponseDto } from '../../calendar/dto/content-calendar.dto';

const trimmedString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);

export class CreateAnnouncementDto {
  @ApiProperty({
    description: 'Unique announcement title for the authenticated user.',
    example: 'Weekly market insights',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  announcement_title!: string;

  @ApiProperty({
    description: 'Announcement body copy shown in the dashboard feed.',
    example: 'Check the new marketing templates and neighborhood reports available this week.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  announcement_content!: string;

  @ApiProperty({
    description: 'Full name from the dashboard form field #Name.40.',
    example: 'Jane Doe',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  full_name!: string;

  @ApiProperty({
    description: 'Email address from the dashboard form.',
    example: 'user@example.com',
    format: 'email',
  })
  @Transform(({ value }: { value: unknown }) => (typeof value === 'string' ? value.trim().toLowerCase() : value))
  @IsEmail({}, { message: 'email must be a valid email address' })
  email!: string;

  @ApiProperty({
    description: 'Phone number from the dashboard form heroicons-outline/megaphone field.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone!: string;

  @ApiPropertyOptional({
    description: 'Optional external link associated with the announcement.',
    example: 'https://example.com/resources/market-insights',
    nullable: true,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string;
}

export class AskDashboardQuestionDto {
  @ApiProperty({
    description: 'Question or prompt submitted to the AI assistant.',
    example: 'Write a short Instagram caption for a new downtown listing.',
    maxLength: 2000,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(2000)
  message!: string;
}

export class DashboardAnnouncementResponseDto {
  @ApiProperty({ description: 'Unique announcement identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Announcement title as stored by the API.', example: 'Weekly market insights' })
  announcement_title!: string;

  @ApiProperty({
    description: 'Announcement content body as stored by the API.',
    example: 'Check the new marketing templates and neighborhood reports available this week.',
  })
  announcement_content!: string;

  @ApiProperty({ description: 'Frontend-friendly title field.', example: 'Weekly market insights' })
  title!: string;

  @ApiProperty({
    description: 'Frontend-friendly message field displayed in the feed.',
    example: 'Check the new marketing templates and neighborhood reports available this week.',
  })
  message!: string;

  @ApiProperty({
    description: 'Frontend-friendly description field displayed in the dashboard UI.',
    example: 'Check the new marketing templates and neighborhood reports available this week.',
  })
  description!: string;

  @ApiProperty({ description: 'Display name associated with the announcement.', example: 'Jane Doe' })
  full_name!: string;

  @ApiProperty({ description: 'Email associated with the announcement.', example: 'user@example.com' })
  email!: string;

  @ApiProperty({ description: 'Phone number associated with the announcement.', example: '+1-555-0100' })
  phone!: string;

  @ApiPropertyOptional({
    description: 'Optional link related to the announcement.',
    example: 'https://example.com/resources/market-insights',
    nullable: true,
  })
  link!: string | null;

  @ApiProperty({ description: 'Announcement lifecycle status for the frontend.', example: 'active' })
  status!: string;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful records always return null.',
    example: null,
    nullable: true,
    type: Object,
  })
  error!: null;

  @ApiProperty({
    description: 'Announcement creation timestamp in ISO 8601 format.',
    example: '2026-06-01T10:00:00.000Z',
  })
  created_at!: string;

  @ApiProperty({
    description: 'Announcement last update timestamp in ISO 8601 format.',
    example: '2026-06-01T10:00:00.000Z',
  })
  updated_at!: string;
}

export class DashboardAnnouncementListDataDto {
  @ApiProperty({ type: [DashboardAnnouncementResponseDto] })
  items!: DashboardAnnouncementResponseDto[];

  @ApiProperty({ description: 'Total number of announcements available for the user.', example: 1 })
  total!: number;
}

export class DashboardAnalyticsMetricsDto {
  @ApiProperty({ description: 'Total AI-assisted content items generated.', example: 12 })
  content_generated!: number;

  @ApiProperty({ description: 'Total downloadable items recorded for the user.', example: 3 })
  downloads!: number;

  @ApiProperty({ description: 'Current used AI credits.', example: 1420 })
  current_ai_credits!: number;

  @ApiProperty({ description: 'Maximum AI credits available to the user.', example: 5000 })
  total_ai_credits!: number;

  @ApiProperty({ description: 'Remaining AI credits after usage.', example: 3580 })
  remaining_ai_credits!: number;
}

export class DashboardAnalyticsResponseDto {
  @ApiProperty({ description: 'Stable analytics resource identifier.', example: 'dashboard_analytics' })
  id!: string;

  @ApiProperty({ description: 'Analytics resource status.', example: 'active' })
  status!: string;

  @ApiProperty({
    description: 'User-facing analytics summary.',
    example: 'Dashboard analytics retrieved successfully',
  })
  description!: string;

  @ApiPropertyOptional({
    description: 'Optional supporting link for analytics resources.',
    example: null,
    nullable: true,
    type: Object,
  })
  link!: null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful analytics responses always return null.',
    example: null,
    nullable: true,
    type: Object,
  })
  error!: null;

  @ApiProperty({ type: DashboardAnalyticsMetricsDto })
  analytics_data!: DashboardAnalyticsMetricsDto;

  @ApiProperty({ description: 'Full name shown in the dashboard greeting.', example: 'Jane Doe' })
  full_name!: string;

  @ApiProperty({ description: 'Email for the authenticated user.', example: 'user@example.com' })
  email!: string;

  @ApiPropertyOptional({
    description: 'Phone number for the authenticated user.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone!: string | null;
}

export class DashboardProfileDto {
  @ApiProperty({ description: 'User identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Dashboard greeting full name.', example: 'Jane Doe' })
  full_name!: string;

  @ApiProperty({ description: 'User email address.', example: 'user@example.com' })
  email!: string;

  @ApiPropertyOptional({ description: 'User phone number when available.', example: '+1-555-0100', nullable: true })
  phone!: string | null;
}

export class DashboardOverviewDataDto {
  @ApiProperty({ type: DashboardProfileDto })
  profile!: DashboardProfileDto;

  @ApiProperty({ type: DashboardAnalyticsResponseDto })
  analytics!: DashboardAnalyticsResponseDto;

  @ApiProperty({ type: [DashboardAnnouncementResponseDto] })
  announcements!: DashboardAnnouncementResponseDto[];

  @ApiProperty({ type: [ContentCalendarEntryResponseDto] })
  content_calendar!: ContentCalendarEntryResponseDto[];

  @ApiProperty({ description: 'Overview resource status.', example: 'active' })
  status!: string;

  @ApiPropertyOptional({
    description: 'Overview resource error field for frontend compatibility.',
    example: null,
    nullable: true,
    type: Object,
  })
  error!: null;

  @ApiPropertyOptional({ description: 'Optional supporting dashboard link.', example: null, nullable: true, type: Object })
  link!: null;

  @ApiProperty({
    description: 'Human-readable overview description for the frontend.',
    example: 'Dashboard overview retrieved successfully',
  })
  description!: string;
}

export class DashboardQuestionResponseDataDto {
  @ApiProperty({
    description: 'Stable generated response identifier.',
    example: 'generated_question_66df0b7814b3e891e4ebcd21',
  })
  id!: string;

  @ApiProperty({ description: 'Response creation status.', example: 'created' })
  status!: string;

  @ApiProperty({ description: 'Frontend title for the generated response.', example: 'AI assistant response' })
  title!: string;

  @ApiProperty({
    description: 'AI assistant response message.',
    example: 'Highlight the listing location, one standout amenity, and a clear call to action in your caption.',
  })
  message!: string;

  @ApiProperty({
    description: 'Detailed AI response text for frontend rendering.',
    example: 'Highlight the listing location, one standout amenity, and a clear call to action in your caption.',
  })
  description!: string;

  @ApiPropertyOptional({ description: 'Optional related resource link.', example: null, nullable: true, type: Object })
  link!: null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful responses always return null.',
    example: null,
    nullable: true,
    type: Object,
  })
  error!: null;

  @ApiProperty({ description: 'Number of AI credits consumed by this request.', example: 1 })
  credits_used!: number;

  @ApiProperty({ description: 'Remaining AI credits after this request.', example: 3579 })
  remaining_ai_credits!: number;
}

export class DashboardOverviewResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ description: 'UI-safe overview message.', example: 'Dashboard overview retrieved successfully' })
  message!: string;

  @ApiProperty({ type: DashboardOverviewDataDto })
  data!: DashboardOverviewDataDto;
}

export class DashboardAnnouncementListResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ description: 'UI-safe list message.', example: 'Announcements retrieved successfully' })
  message!: string;

  @ApiProperty({ type: DashboardAnnouncementListDataDto })
  data!: DashboardAnnouncementListDataDto;
}

export class DashboardAnnouncementCreateResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ description: 'UI-safe create message.', example: 'Announcement created successfully' })
  message!: string;

  @ApiProperty({ type: DashboardAnnouncementResponseDto })
  data!: DashboardAnnouncementResponseDto;
}

export class DashboardAnalyticsEnvelopeResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ description: 'UI-safe analytics message.', example: 'Dashboard analytics retrieved successfully' })
  message!: string;

  @ApiProperty({ type: DashboardAnalyticsResponseDto })
  data!: DashboardAnalyticsResponseDto;
}

export class DashboardQuestionResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ description: 'UI-safe AI generation message.', example: 'Question answered successfully' })
  message!: string;

  @ApiProperty({ type: DashboardQuestionResponseDataDto })
  data!: DashboardQuestionResponseDataDto;
}

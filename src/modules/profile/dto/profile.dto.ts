import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import {
  IsEmail,
  IsInt,
  IsNotEmpty,
  IsMongoId,
  IsOptional,
  IsString,
  IsUrl,
  Length,
  Matches,
  Max,
  Min,
} from 'class-validator';

const PHONE_REGEX = /^\+?[0-9][0-9\s\-().]{6,24}$/;
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/;

const trimString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);
const normalizeEmail = ({ value }: { value: unknown }): unknown =>
  typeof value === 'string' ? value.trim().toLowerCase() : value;

export class ProfileAddressDto {
  @ApiPropertyOptional({ description: 'Street address line.', example: '123 Main St', nullable: true })
  street!: string | null;

  @ApiPropertyOptional({ description: 'City name.', example: 'Washington', nullable: true })
  city!: string | null;

  @ApiPropertyOptional({ description: 'State, province, or region.', example: 'DC', nullable: true })
  state!: string | null;

  @ApiPropertyOptional({ description: 'ZIP or postal code.', example: '20001', nullable: true })
  zip!: string | null;

  @ApiPropertyOptional({ description: 'Country name.', example: 'USA', nullable: true })
  country!: string | null;
}

export class ProfileSummaryDto {
  @ApiPropertyOptional({
    description: 'Short profile summary displayed in profile widgets.',
    example: 'How you show up across the studio.',
    nullable: true,
  })
  bio!: string | null;

  @ApiPropertyOptional({
    description: 'Long-form description field mirrored for frontend compatibility.',
    example: 'How you show up across the studio.',
    nullable: true,
  })
  description!: string | null;

  @ApiPropertyOptional({
    description: 'URL of the user profile image.',
    example: 'https://cdn.example.com/profiles/joseph-stanley.png',
    nullable: true,
  })
  image!: string | null;

  @ApiProperty({ description: 'Derived profile display name.', example: 'Joseph Stanley' })
  name!: string;
}

export class DownloadHistoryItemDto {
  @ApiProperty({ description: 'Unique download history identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({
    description: 'User-facing resource title shown in the download history list.',
    example: 'Luxury Listing Guide - 2026',
  })
  title!: string;

  @ApiProperty({ description: 'Normalized frontend-friendly title alias.', example: 'Luxury Listing Guide - 2026' })
  name!: string;

  @ApiProperty({ description: 'Type of downloadable asset.', example: 'PDF' })
  file_type!: string;

  @ApiProperty({ description: 'Human-readable file size string.', example: '4.2 MB' })
  file_size!: string;

  @ApiProperty({
    description: 'Date of the last download in YYYY-MM-DD format for the frontend list.',
    example: '2026-06-04',
  })
  last_downloaded!: string;

  @ApiProperty({
    description: 'More detailed timestamp for audit-friendly clients.',
    example: '2026-06-04T12:30:00.000Z',
  })
  downloaded_at!: string;

  @ApiProperty({ description: 'Lifecycle status of the download history record.', example: 'active' })
  status!: string;

  @ApiPropertyOptional({
    description: 'Optional download URL or deep link to the resource.',
    example: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
    nullable: true,
  })
  link!: string | null;

  @ApiProperty({
    description: 'UI-safe message for the download item.',
    example: 'Download available for re-download',
  })
  message!: string;

  @ApiProperty({
    description: 'UI-safe description of the downloadable resource.',
    example: 'Luxury Listing Guide - 2026 (PDF, 4.2 MB)',
  })
  description!: string;

  @ApiPropertyOptional({
    description: 'Frontend compatibility error field. Successful records always return null.',
    example: null,
    nullable: true,
  })
  error!: null;
}

export class DownloadHistoryPaginationDto {
  @ApiProperty({ description: 'Current page number.', example: 1 })
  page!: number;

  @ApiProperty({ description: 'Maximum number of items returned per page.', example: 10 })
  limit!: number;

  @ApiProperty({ description: 'Total number of active download records available.', example: 2 })
  total!: number;

  @ApiProperty({ description: 'Total number of pages available.', example: 1 })
  total_pages!: number;

  @ApiProperty({ description: 'Whether a subsequent page exists.', example: false })
  has_next_page!: boolean;

  @ApiProperty({ description: 'Whether a previous page exists.', example: false })
  has_previous_page!: boolean;
}

export class DownloadsProfileSummaryDto {
  @ApiProperty({ description: 'Authenticated user identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Display name for the downloads screen header.', example: 'Jane Doe' })
  name!: string;

  @ApiProperty({ description: 'Frontend-friendly full name field from Figma.', example: 'Jane Doe' })
  full_name!: string;

  @ApiPropertyOptional({
    description: 'Phone number shown in the downloads screen header.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone!: string | null;
}

export class DownloadsResponseDataDto {
  @ApiProperty({ description: 'Stable downloads resource identifier.', example: 'profile_downloads' })
  id!: string;

  @ApiProperty({ description: 'Downloads screen title.', example: 'Download history' })
  title!: string;

  @ApiProperty({ description: 'Display name alias for the authenticated user.', example: 'Jane Doe' })
  name!: string;

  @ApiProperty({ description: 'Full name from the downloads Figma contract.', example: 'Jane Doe' })
  full_name!: string;

  @ApiPropertyOptional({
    description: 'Phone number from the downloads Figma contract.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone!: string | null;

  @ApiProperty({
    description: 'UI-safe message describing the successful response.',
    example: 'Download history retrieved successfully',
  })
  message!: string;

  @ApiProperty({
    description: 'Detailed description suitable for the frontend empty or loaded state.',
    example: 'Active download history for the authenticated user',
  })
  description!: string;

  @ApiProperty({ type: DownloadsProfileSummaryDto })
  profile!: DownloadsProfileSummaryDto;

  @ApiProperty({ type: [DownloadHistoryItemDto] })
  downloads!: DownloadHistoryItemDto[];

  @ApiProperty({ type: DownloadHistoryPaginationDto })
  pagination!: DownloadHistoryPaginationDto;

  @ApiPropertyOptional({
    description: 'Optional supporting link for the downloads screen.',
    example: null,
    nullable: true,
  })
  link!: null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility error field. Successful responses always return null.',
    example: null,
    nullable: true,
  })
  error!: null;
}

export class DownloadsResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Download history retrieved successfully' })
  message!: string;

  @ApiProperty({ type: DownloadsResponseDataDto })
  data!: DownloadsResponseDataDto;
}

export class RedownloadResponseDataDto {
  @ApiProperty({ description: 'Stable re-download action identifier.', example: 'profile_download_redownload' })
  id!: string;

  @ApiProperty({ description: 'Action title for the frontend.', example: 'Re-download ready' })
  title!: string;

  @ApiProperty({ description: 'Resource title for the requested download.', example: 'Luxury Listing Guide - 2026' })
  name!: string;

  @ApiProperty({ description: 'Requested download title.', example: 'Luxury Listing Guide - 2026' })
  full_name!: string;

  @ApiProperty({ description: 'Phone number echoed from the typed request body.', example: '+1-555-0100' })
  phone!: string;

  @ApiProperty({
    description: 'UI-safe success message for the action result.',
    example: 'Re-download prepared successfully',
  })
  message!: string;

  @ApiProperty({
    description: 'Detailed description of the re-download result.',
    example: 'The selected file is ready to be downloaded again',
  })
  description!: string;

  @ApiProperty({ type: DownloadHistoryItemDto })
  download!: DownloadHistoryItemDto;

  @ApiPropertyOptional({
    description: 'Optional direct link to the downloadable resource.',
    example: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
    nullable: true,
  })
  link!: string | null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility error field. Successful responses always return null.',
    example: null,
    nullable: true,
  })
  error!: null;
}

export class RedownloadResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Re-download prepared successfully' })
  message!: string;

  @ApiProperty({ type: RedownloadResponseDataDto })
  data!: RedownloadResponseDataDto;
}

export class ProfileResponseDataDto {
  @ApiProperty({ description: 'Public user identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Display name assembled from first and last name.', example: 'Joseph Stanley' })
  name!: string;

  @ApiProperty({ description: 'Frontend-friendly full name field.', example: 'Joseph Stanley' })
  full_name!: string;

  @ApiProperty({ description: 'First name.', example: 'Joseph' })
  first_name!: string;

  @ApiProperty({ description: 'Last name.', example: 'Stanley' })
  last_name!: string;

  @ApiProperty({ description: 'Profile email address.', example: 'joseph.stanley@example.com' })
  email!: string;

  @ApiPropertyOptional({
    description: 'Primary mobile number shown on the profile screen.',
    example: '123-456-7890',
    nullable: true,
  })
  mobile_number!: string | null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility alias for the mobile number.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone!: string | null;

  @ApiPropertyOptional({
    description: 'User biography text.',
    example: 'How you show up across the studio.',
    nullable: true,
  })
  bio!: string | null;

  @ApiPropertyOptional({
    description: 'Long-form description mirrored from bio for frontend compatibility.',
    example: 'How you show up across the studio.',
    nullable: true,
  })
  description!: string | null;

  @ApiPropertyOptional({
    description: 'Human-readable time zone label.',
    example: 'Washington, DC, USA (GMT-4)',
    nullable: true,
  })
  time_zone!: string | null;

  @ApiPropertyOptional({ description: 'Street address line.', example: '123 Main St', nullable: true })
  street!: string | null;

  @ApiPropertyOptional({ description: 'Country name.', example: 'USA', nullable: true })
  country!: string | null;

  @ApiPropertyOptional({ description: 'State, province, or region.', example: 'DC', nullable: true })
  state!: string | null;

  @ApiPropertyOptional({ description: 'City name.', example: 'Washington', nullable: true })
  city!: string | null;

  @ApiPropertyOptional({ description: 'ZIP or postal code.', example: '20001', nullable: true })
  zip!: string | null;

  @ApiPropertyOptional({
    description: 'Single-line address string assembled for the frontend.',
    example: '123 Main St, Washington, DC 20001, USA',
    nullable: true,
  })
  address!: string | null;

  @ApiProperty({
    description: 'Structured profile summary used by the frontend profile card.',
    type: ProfileSummaryDto,
  })
  profile!: ProfileSummaryDto;

  @ApiProperty({
    description: 'Structured address object for frontend convenience.',
    type: ProfileAddressDto,
  })
  address_details!: ProfileAddressDto;

  @ApiPropertyOptional({
    description: 'Public image URL for avatar rendering.',
    example: 'https://cdn.example.com/profiles/joseph-stanley.png',
    nullable: true,
  })
  image!: string | null;

  @ApiPropertyOptional({
    description: 'Optional external profile or website link.',
    example: 'https://agentwise.example.com/joseph-stanley',
    nullable: true,
  })
  link!: string | null;

  @ApiPropertyOptional({
    description: 'Compatibility field reserved for per-record errors. Successful responses return null.',
    example: null,
    nullable: true,
  })
  error!: string | null;
}

export class ProfileResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Profile retrieved successfully' })
  message!: string;

  @ApiProperty({ type: ProfileResponseDataDto })
  data!: ProfileResponseDataDto;
}

export class ContentGeneratedItemDto {
  @ApiProperty({ description: 'Unique generated content identifier.', example: '66df0b7814b3e891e4ebcd51' })
  id!: string;

  @ApiProperty({
    description: 'Stable alias for the generated content identifier used by the frontend contract.',
    example: '66df0b7814b3e891e4ebcd51',
  })
  content_id!: string;

  @ApiProperty({ description: 'Generated content title.', example: 'Luxury Condo Social Caption' })
  title!: string;

  @ApiProperty({
    description: 'Generated content body or summary shown in the content history list.',
    example: 'Fresh social caption promoting a luxury condo open house in Miami.',
  })
  description!: string;

  @ApiProperty({
    description: 'Creation timestamp in ISO 8601 format.',
    example: '2026-08-18T09:30:00.000Z',
    format: 'date-time',
  })
  created_at!: string;

  @ApiProperty({
    description: 'Last update timestamp in ISO 8601 format.',
    example: '2026-08-18T10:15:00.000Z',
    format: 'date-time',
  })
  updated_at!: string;

  @ApiProperty({ description: 'Full name from the Profile Content Generated form field #Name.40.', example: 'Jane Doe' })
  full_name!: string;

  @ApiProperty({
    description: 'Phone number from the Profile Content Generated form field heroicons-outline/megaphone.',
    example: '+1-555-0100',
  })
  phone!: string;

  @ApiProperty({
    description: 'Structured profile summary associated with the generated content item.',
    type: DownloadsProfileSummaryDto,
  })
  profile!: DownloadsProfileSummaryDto;

  @ApiPropertyOptional({
    description: 'Optional deep link to the generated content resource.',
    example: null,
    nullable: true,
  })
  link!: string | null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful items always return null.',
    example: null,
    nullable: true,
  })
  error!: null;
}

export class AiCreditUsageDto {
  @ApiProperty({ description: 'Total AI credits available to the authenticated user.', example: 5000 })
  total_ai_credits!: number;

  @ApiProperty({ description: 'AI credits already consumed by the authenticated user.', example: 125 })
  used_ai_credits!: number;

  @ApiProperty({ description: 'AI credits still available to the authenticated user.', example: 4875 })
  remaining_ai_credits!: number;
}

export class ContentGeneratedResponseDataDto {
  @ApiProperty({ description: 'Stable content history resource identifier.', example: 'profile_content_generated' })
  id!: string;

  @ApiProperty({ description: 'Content Generated screen title.', example: 'Content history' })
  title!: string;

  @ApiProperty({
    description: 'UI-safe message describing the list retrieval result.',
    example: 'Generated content retrieved successfully',
  })
  message!: string;

  @ApiProperty({
    description: 'Detailed description for the content history section.',
    example: 'Generated content history for the authenticated user',
  })
  description!: string;

  @ApiProperty({ description: 'Display name alias for the authenticated user.', example: 'Jane Doe' })
  name!: string;

  @ApiProperty({ description: 'Full name from the content-generated frontend contract.', example: 'Jane Doe' })
  full_name!: string;

  @ApiPropertyOptional({
    description: 'Phone number shown in the content-generated header area.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone!: string | null;

  @ApiProperty({ type: DownloadsProfileSummaryDto })
  profile!: DownloadsProfileSummaryDto;

  @ApiProperty({ type: [ContentGeneratedItemDto] })
  contents!: ContentGeneratedItemDto[];

  @ApiProperty({ type: AiCreditUsageDto })
  ai_credit_usage!: AiCreditUsageDto;

  @ApiPropertyOptional({
    description: 'Optional supporting link for the Content Generated screen.',
    example: null,
    nullable: true,
  })
  link!: null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful responses always return null.',
    example: null,
    nullable: true,
  })
  error!: null;
}

export class ContentGeneratedResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Generated content retrieved successfully' })
  message!: string;

  @ApiProperty({ type: ContentGeneratedResponseDataDto })
  data!: ContentGeneratedResponseDataDto;
}

export class ContentGeneratedMutationResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Generated content created successfully' })
  message!: string;

  @ApiProperty({ type: ContentGeneratedItemDto })
  data!: ContentGeneratedItemDto;
}

export class ChangePasswordResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Password changed successfully' })
  message!: string;

  @ApiProperty({
    example: {},
    description: 'Empty data object returned after a successful password change.',
  })
  data!: Record<string, never>;
}

export class CreateProfileContentDto {
  @ApiProperty({
    description: 'Generated content title shown in the content history list.',
    example: 'Luxury Condo Social Caption',
    minLength: 1,
    maxLength: 160,
  })
  @Transform(trimString)
  @IsString({ message: 'title must be a string' })
  @IsNotEmpty({ message: 'title is required' })
  @Length(1, 160, { message: 'title must be between 1 and 160 characters' })
  title!: string;

  @ApiProperty({
    description: 'Generated content description or body shown to the user.',
    example: 'Fresh social caption promoting a luxury condo open house in Miami.',
    minLength: 1,
    maxLength: 2000,
  })
  @Transform(trimString)
  @IsString({ message: 'description must be a string' })
  @IsNotEmpty({ message: 'description is required' })
  @Length(1, 2000, { message: 'description must be between 1 and 2000 characters' })
  description!: string;

  @ApiProperty({
    description: 'Full name from the content-generated form field #Name.40.',
    example: 'Jane Doe',
    minLength: 1,
    maxLength: 160,
  })
  @Transform(trimString)
  @IsString({ message: 'full_name must be a string' })
  @IsNotEmpty({ message: 'full_name is required' })
  @Length(1, 160, { message: 'full_name must be between 1 and 160 characters' })
  full_name!: string;

  @ApiProperty({
    description: 'Phone number from the content-generated form field heroicons-outline/megaphone.',
    example: '+1-555-0100',
  })
  @Transform(trimString)
  @Matches(PHONE_REGEX, { message: 'phone must be a valid phone number' })
  phone!: string;

  @ApiPropertyOptional({
    description: 'Optional deep link to the generated content record or asset.',
    example: 'https://agentwise.example.com/content/luxury-condo-social-caption',
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsUrl({}, { message: 'link must be a valid URL' })
  link?: string | null;
}

export class UpdateProfileContentDto extends CreateProfileContentDto {}

export class GetDownloadsQueryDto {
  @ApiPropertyOptional({
    description: 'Page number for paginated download history results.',
    example: 1,
    minimum: 1,
    default: 1,
  })
  @Transform(({ value }: { value: unknown }) => (value === undefined ? 1 : Number(value)))
  @IsInt({ message: 'page must be an integer number' })
  @Min(1, { message: 'page must be greater than or equal to 1' })
  page = 1;

  @ApiPropertyOptional({
    description: 'Maximum number of download records to return per page.',
    example: 10,
    minimum: 1,
    maximum: 50,
    default: 10,
  })
  @Transform(({ value }: { value: unknown }) => (value === undefined ? 10 : Number(value)))
  @IsInt({ message: 'limit must be an integer number' })
  @Min(1, { message: 'limit must be greater than or equal to 1' })
  @Max(50, { message: 'limit must be less than or equal to 50' })
  limit = 10;
}

export class RedownloadDto {
  @ApiProperty({
    description: 'Download history record identifier to re-download.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @IsMongoId({ message: 'download_id must be a valid MongoDB ObjectId' })
  download_id!: string;

  @ApiProperty({
    description: 'Full name from the downloads form field #Name.40.',
    example: 'Jane Doe',
    minLength: 1,
    maxLength: 160,
  })
  @Transform(trimString)
  @IsString({ message: 'full_name must be a string' })
  @IsNotEmpty({ message: 'full_name is required' })
  @Length(1, 160, { message: 'full_name must be between 1 and 160 characters' })
  full_name!: string;

  @ApiProperty({
    description: 'Phone number from the downloads form field heroicons-outline/megaphone.',
    example: '+1-555-0100',
  })
  @Transform(trimString)
  @Matches(PHONE_REGEX, { message: 'phone must be a valid phone number' })
  phone!: string;
}

export class UpdateProfileDto {
  @ApiProperty({
    description: 'First name displayed on the profile screen.',
    example: 'Joseph',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(trimString)
  @IsString({ message: 'first_name must be a string' })
  @IsNotEmpty({ message: 'first_name is required' })
  @Length(1, 100, { message: 'first_name must be between 1 and 100 characters' })
  first_name!: string;

  @ApiProperty({
    description: 'Last name displayed on the profile screen.',
    example: 'Stanley',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(trimString)
  @IsString({ message: 'last_name must be a string' })
  @IsNotEmpty({ message: 'last_name is required' })
  @Length(1, 100, { message: 'last_name must be between 1 and 100 characters' })
  last_name!: string;

  @ApiProperty({
    description: 'Unique email address for the account.',
    example: 'joseph.stanley@example.com',
    format: 'email',
  })
  @Transform(normalizeEmail)
  @IsEmail({}, { message: 'email must be a valid email address' })
  @Length(1, 254, { message: 'email must be at most 254 characters' })
  email!: string;

  @ApiPropertyOptional({
    description: 'Primary mobile number shown on the profile screen.',
    example: '123-456-7890',
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @Matches(PHONE_REGEX, { message: 'mobile_number must be a valid phone number' })
  mobile_number?: string | null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility alias for the mobile number field from Figma.',
    example: '+1-555-0100',
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @Matches(PHONE_REGEX, { message: 'phone must be a valid phone number' })
  phone?: string | null;

  @ApiPropertyOptional({
    description: 'User biography or tagline.',
    example: 'How you show up across the studio.',
    maxLength: 500,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'bio must be a string' })
  @Length(0, 500, { message: 'bio must be at most 500 characters' })
  bio?: string | null;

  @ApiPropertyOptional({
    description: 'Human-readable time zone label selected by the user.',
    example: 'Washington, DC, USA (GMT-4)',
    maxLength: 120,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'time_zone must be a string' })
  @Length(0, 120, { message: 'time_zone must be at most 120 characters' })
  time_zone?: string | null;

  @ApiPropertyOptional({
    description: 'Street address line.',
    example: '123 Main St',
    maxLength: 200,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'street must be a string' })
  @Length(0, 200, { message: 'street must be at most 200 characters' })
  street?: string | null;

  @ApiPropertyOptional({
    description: 'Country name.',
    example: 'USA',
    maxLength: 100,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'country must be a string' })
  @Length(0, 100, { message: 'country must be at most 100 characters' })
  country?: string | null;

  @ApiPropertyOptional({
    description: 'State, province, or region.',
    example: 'DC',
    maxLength: 100,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'state must be a string' })
  @Length(0, 100, { message: 'state must be at most 100 characters' })
  state?: string | null;

  @ApiPropertyOptional({
    description: 'City name.',
    example: 'Washington',
    maxLength: 100,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'city must be a string' })
  @Length(0, 100, { message: 'city must be at most 100 characters' })
  city?: string | null;

  @ApiPropertyOptional({
    description: 'ZIP or postal code.',
    example: '20001',
    maxLength: 20,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'zip must be a string' })
  @Length(0, 20, { message: 'zip must be at most 20 characters' })
  zip?: string | null;

  @ApiPropertyOptional({
    description: 'Optional avatar image URL.',
    example: 'https://cdn.example.com/profiles/joseph-stanley.png',
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsUrl({}, { message: 'image must be a valid URL' })
  image?: string | null;

  @ApiPropertyOptional({
    description: 'Optional external profile or website link.',
    example: 'https://agentwise.example.com/joseph-stanley',
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsUrl({}, { message: 'link must be a valid URL' })
  link?: string | null;

  @ApiPropertyOptional({
    description: 'Optional description field mirrored to the frontend.',
    example: 'How you show up across the studio.',
    maxLength: 500,
    nullable: true,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString({ message: 'description must be a string' })
  @Length(0, 500, { message: 'description must be at most 500 characters' })
  description?: string | null;
}

export class ChangePasswordDto {
  @ApiProperty({
    description: 'Current account password.',
    example: 'StrongPassword123!',
    format: 'password',
    writeOnly: true,
  })
  @IsString({ message: 'current_password must be a string' })
  @IsNotEmpty({ message: 'current_password is required' })
  current_password!: string;

  @ApiProperty({
    description: 'New password to store for the account.',
    example: 'NewStrongPassword456!',
    format: 'password',
    minLength: 8,
    writeOnly: true,
  })
  @IsString({ message: 'new_password must be a string' })
  @Matches(PASSWORD_REGEX, {
    message:
      'new_password must be at least 8 characters and include an uppercase letter, lowercase letter, number, and special character',
  })
  new_password!: string;

  @ApiProperty({
    description: 'Password confirmation to prevent accidental updates.',
    example: 'NewStrongPassword456!',
    format: 'password',
    writeOnly: true,
  })
  @IsString({ message: 'confirm_password must be a string' })
  @IsNotEmpty({ message: 'confirm_password is required' })
  confirm_password!: string;
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform, Type } from 'class-transformer';
import {
  Equals,
  IsBoolean,
  IsEmail,
  IsInt,
  IsNotEmpty,
  IsOptional,
  IsString,
  Length,
  Matches,
  MaxLength,
  Min,
} from 'class-validator';

const PHONE_REGEX = /^\+?[0-9][0-9\s\-().]{6,24}$/;

const trimmedString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);

const normalizeEmail = ({ value }: { value: unknown }): unknown =>
  typeof value === 'string' ? value.trim().toLowerCase() : value;

const composeFullName = ({ value, obj }: { value: unknown; obj: Record<string, unknown> }): unknown => {
  const trimmed = typeof value === 'string' ? value.trim() : value;
  if (typeof trimmed === 'string' && trimmed.length > 0) {
    return trimmed;
  }

  const first = typeof obj.first_name === 'string' ? obj.first_name.trim() : '';
  const last = typeof obj.last_name === 'string' ? obj.last_name.trim() : '';
  const composed = `${first} ${last}`.trim();
  return composed.length > 0 ? composed : trimmed;
};

const resolvePhone = ({ value, obj }: { value: unknown; obj: Record<string, unknown> }): unknown => {
  const trimmed = typeof value === 'string' ? value.trim() : value;
  if (typeof trimmed === 'string' && trimmed.length > 0) {
    return trimmed;
  }

  return typeof obj.phone_number === 'string' ? obj.phone_number.trim() : trimmed;
};

export class VisitorHomeSearchQueryDto {
  @ApiPropertyOptional({
    description: 'Free-text search term matched against title, description, category, and tags.',
    example: 'templates',
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(120)
  q?: string;

  @ApiPropertyOptional({
    description: 'Optional category filter.',
    example: 'Social Media',
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(120)
  category?: string;

  @ApiPropertyOptional({
    description: 'Page number for paginated results.',
    example: 1,
    default: 1,
  })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(1)
  page = 1;

  @ApiPropertyOptional({
    description: 'Maximum number of items returned per page.',
    example: 10,
    default: 10,
  })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(1)
  limit = 10;
}

export class VisitorHomeSubscribeDto {
  @ApiPropertyOptional({
    description: 'Visitor given name from the Home screen First Name field.',
    example: 'Jane',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString({ message: 'first_name must be a string' })
  @IsNotEmpty({ message: 'first_name is required' })
  @Length(1, 100, { message: 'first_name must be between 1 and 100 characters' })
  first_name?: string;

  @ApiPropertyOptional({
    description: 'Visitor family name from the Home screen Last Name field.',
    example: 'Doe',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString({ message: 'last_name must be a string' })
  @IsNotEmpty({ message: 'last_name is required' })
  @Length(1, 100, { message: 'last_name must be between 1 and 100 characters' })
  last_name?: string;

  @ApiProperty({
    description: 'Full name from the Figma form field #Name.40. Composed from first_name and last_name when omitted.',
    example: 'Jane Doe',
    minLength: 1,
    maxLength: 160,
  })
  @Transform(composeFullName)
  @IsOptional()
  @IsString({ message: 'full_name must be a string' })
  @IsNotEmpty({ message: 'full_name is required' })
  @Length(1, 160, { message: 'full_name must be between 1 and 160 characters' })
  full_name?: string;

  @ApiProperty({
    description: 'Email address used for marketing subscription.',
    example: 'jane.doe@example.com',
    format: 'email',
  })
  @Transform(normalizeEmail)
  @IsEmail({}, { message: 'email must be a valid email address' })
  @Length(1, 254, { message: 'email must be at most 254 characters' })
  email!: string;

  @ApiPropertyOptional({
    description: 'Phone number alias from the Home screen Phone number field. Copied onto phone when phone is omitted.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @IsOptional()
  @Matches(PHONE_REGEX, { message: 'phone_number must be a valid phone number' })
  phone_number?: string;

  @ApiProperty({
    description: 'Phone number from the Figma megaphone field. Accepts phone_number as an alias.',
    example: '+1-555-0100',
  })
  @Transform(resolvePhone)
  @IsOptional()
  @IsString({ message: 'phone must be a string' })
  @IsNotEmpty({ message: 'phone is required' })
  @Matches(PHONE_REGEX, { message: 'phone must be a valid phone number' })
  phone?: string;

  @ApiProperty({
    description: 'Must be true to confirm acceptance of the Privacy Policy and Terms of Service.',
    example: true,
  })
  @IsBoolean({ message: 'terms_accepted must be a boolean' })
  @Equals(true, { message: 'terms_accepted must be true' })
  terms_accepted!: boolean;
}

export class VisitorHomeTermsAcceptanceDto {
  @ApiPropertyOptional({
    description: 'Visitor given name from the Home screen First Name field.',
    example: 'Jane',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString({ message: 'first_name must be a string' })
  @IsNotEmpty({ message: 'first_name is required' })
  @Length(1, 100, { message: 'first_name must be between 1 and 100 characters' })
  first_name?: string;

  @ApiPropertyOptional({
    description: 'Visitor family name from the Home screen Last Name field.',
    example: 'Doe',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString({ message: 'last_name must be a string' })
  @IsNotEmpty({ message: 'last_name is required' })
  @Length(1, 100, { message: 'last_name must be between 1 and 100 characters' })
  last_name?: string;

  @ApiPropertyOptional({
    description: 'Full name from the Figma form field #Name.40. Composed from first_name and last_name when omitted.',
    example: 'Jane Doe',
    minLength: 1,
    maxLength: 160,
  })
  @Transform(composeFullName)
  @IsOptional()
  @IsString({ message: 'full_name must be a string' })
  @IsNotEmpty({ message: 'full_name is required' })
  @Length(1, 160, { message: 'full_name must be between 1 and 160 characters' })
  full_name?: string;

  @ApiProperty({
    description: 'Email address associated with the terms and privacy acceptance.',
    example: 'jane.doe@example.com',
    format: 'email',
  })
  @Transform(normalizeEmail)
  @IsEmail({}, { message: 'email must be a valid email address' })
  @Length(1, 254, { message: 'email must be at most 254 characters' })
  email!: string;

  @ApiPropertyOptional({
    description: 'Phone number alias from the Home screen Phone number field. Copied onto phone when phone is omitted.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @IsOptional()
  @Matches(PHONE_REGEX, { message: 'phone_number must be a valid phone number' })
  phone_number?: string;

  @ApiPropertyOptional({
    description: 'Phone number from the Figma megaphone field. Accepts phone_number as an alias.',
    example: '+1-555-0100',
  })
  @Transform(resolvePhone)
  @IsOptional()
  @IsString({ message: 'phone must be a string' })
  @IsNotEmpty({ message: 'phone is required' })
  @Matches(PHONE_REGEX, { message: 'phone must be a valid phone number' })
  phone?: string;

  @ApiProperty({
    description: 'Must be true to confirm acceptance of the Privacy Policy and Terms of Service.',
    example: true,
  })
  @IsBoolean({ message: 'terms_accepted must be a boolean' })
  @Equals(true, { message: 'terms_accepted must be true' })
  terms_accepted!: boolean;
}

export class VisitorHomeContentItemResponseDto {
  @ApiProperty({ description: 'Unique public content identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({
    description: 'Frontend display name aliased from the content title.',
    example: 'Luxury Listing Social Template',
  })
  name!: string;

  @ApiProperty({
    description: 'Content title displayed on the visitor Home screen.',
    example: 'Luxury Listing Social Template',
  })
  title!: string;

  @ApiProperty({
    description: 'Marketing description shown in Home search and browse results.',
    example: 'Help real estate professionals create content faster with ready-made templates.',
  })
  description!: string;

  @ApiProperty({
    description: 'Destination link for Download or Customize actions.',
    example: 'https://example.com/visitor/home/luxury-listing-template',
  })
  link!: string;

  @ApiProperty({
    description: 'Preview image URL for the content card.',
    example: 'https://cdn.example.com/visitor/home/luxury-listing-template.jpg',
  })
  image!: string;

  @ApiProperty({
    description: 'Original stored image URL retained for backend consumers.',
    example: 'https://cdn.example.com/visitor/home/luxury-listing-template.jpg',
  })
  image_url!: string;

  @ApiProperty({ description: 'Category label used for grouping marketing content.', example: 'Social Media' })
  category!: string;

  @ApiProperty({
    description: 'Searchable tag labels.',
    example: ['templates', 'instagram', 'listing'],
    type: [String],
  })
  tags!: string[];

  @ApiPropertyOptional({
    description: 'Full name is not attached to public content items.',
    example: null,
    nullable: true,
  })
  full_name!: string | null;

  @ApiPropertyOptional({
    description: 'First name is not attached to public content items.',
    example: null,
    nullable: true,
  })
  first_name!: string | null;

  @ApiPropertyOptional({
    description: 'Last name is not attached to public content items.',
    example: null,
    nullable: true,
  })
  last_name!: string | null;

  @ApiPropertyOptional({ description: 'Email is not attached to public content items.', example: null, nullable: true })
  email!: string | null;

  @ApiPropertyOptional({ description: 'Phone is not attached to public content items.', example: null, nullable: true })
  phone!: string | null;

  @ApiPropertyOptional({
    description: 'Phone number alias is not attached to public content items.',
    example: null,
    nullable: true,
  })
  phone_number!: string | null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful items always return null.',
    example: null,
    nullable: true,
    type: Object,
  })
  error!: null;

  @ApiProperty({ description: 'Whether the content item is active and visible on the Home screen.', example: true })
  is_active!: boolean;

  @ApiProperty({ description: 'Creation timestamp in ISO 8601 format.', example: '2026-06-01T10:00:00.000Z' })
  created_at!: string;

  @ApiProperty({ description: 'Last update timestamp in ISO 8601 format.', example: '2026-06-02T12:30:00.000Z' })
  updated_at!: string;
}

export class VisitorHomePaginationDto {
  @ApiProperty({ example: 1 })
  page!: number;

  @ApiProperty({ example: 10 })
  limit!: number;

  @ApiProperty({ example: 1 })
  total!: number;

  @ApiProperty({ example: 1 })
  total_pages!: number;

  @ApiProperty({ example: false })
  has_next_page!: boolean;

  @ApiProperty({ example: false })
  has_previous_page!: boolean;
}

export class VisitorHomeSearchDataDto {
  @ApiProperty({ type: [VisitorHomeContentItemResponseDto] })
  items!: VisitorHomeContentItemResponseDto[];

  @ApiProperty({ type: VisitorHomePaginationDto })
  pagination!: VisitorHomePaginationDto;
}

export class VisitorHomeSearchResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Visitor home search completed successfully' })
  message!: string;

  @ApiProperty({ type: VisitorHomeSearchDataDto })
  data!: VisitorHomeSearchDataDto;
}

export class VisitorHomeLeadResponseDto {
  @ApiProperty({ description: 'Unique visitor lead identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Display name assembled from the submitted name fields.', example: 'Jane Doe' })
  name!: string;

  @ApiProperty({ description: 'Full name from the Figma #Name.40 field.', example: 'Jane Doe' })
  full_name!: string;

  @ApiPropertyOptional({ description: 'Visitor given name.', example: 'Jane', nullable: true })
  first_name!: string | null;

  @ApiPropertyOptional({ description: 'Visitor family name.', example: 'Doe', nullable: true })
  last_name!: string | null;

  @ApiProperty({ description: 'Marketing email address.', example: 'jane.doe@example.com' })
  email!: string;

  @ApiPropertyOptional({
    description: 'Phone number from the Figma megaphone field.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone!: string | null;

  @ApiPropertyOptional({
    description: 'Frontend phone_number alias mirrored from phone.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone_number!: string | null;

  @ApiPropertyOptional({
    description: 'Optional content link. Visitor leads do not attach a resource link.',
    example: null,
    nullable: true,
  })
  link!: string | null;

  @ApiPropertyOptional({
    description: 'Optional description. Visitor leads do not attach marketing copy.',
    example: null,
    nullable: true,
  })
  description!: string | null;

  @ApiProperty({ description: 'Whether the Privacy Policy and Terms of Service were accepted.', example: true })
  terms_accepted!: boolean;

  @ApiProperty({ description: 'Whether the visitor is subscribed to marketing email.', example: true })
  subscribed!: boolean;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful leads always return null.',
    example: null,
    nullable: true,
    type: Object,
  })
  error!: null;

  @ApiProperty({ description: 'Creation timestamp in ISO 8601 format.', example: '2026-06-01T10:00:00.000Z' })
  created_at!: string;

  @ApiProperty({ description: 'Last update timestamp in ISO 8601 format.', example: '2026-06-02T12:30:00.000Z' })
  updated_at!: string;
}

export class VisitorHomeSubscribeResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Subscribed successfully' })
  message!: string;

  @ApiProperty({ type: VisitorHomeLeadResponseDto })
  data!: VisitorHomeLeadResponseDto;
}

export class VisitorHomeTermsAcceptanceResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Terms and privacy policy accepted successfully' })
  message!: string;

  @ApiProperty({ type: VisitorHomeLeadResponseDto })
  data!: VisitorHomeLeadResponseDto;
}

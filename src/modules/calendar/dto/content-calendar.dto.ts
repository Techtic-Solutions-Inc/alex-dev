import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { IsDateString, IsNotEmpty, IsOptional, IsString, IsUrl, Matches, MaxLength } from 'class-validator';

const trimmedString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);

export class CreateContentCalendarEntryDto {
  @ApiProperty({
    description: 'Short title shown for the scheduled content item.',
    example: 'Market update - Austin Q2',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  title!: string;

  @ApiProperty({
    description: 'Scheduled publish date and time in ISO 8601 format.',
    example: '2026-06-15T00:00:00Z',
    format: 'date-time',
  })
  @IsDateString()
  date!: string;

  @ApiProperty({
    description:
      'Full content body for the calendar entry. This is also exposed as the frontend-friendly description field.',
    example:
      'Your personal content calendar designed to grow your business - made specifically for you. Drag, drop, edit, and curate your perfect content strategy or feel free to use this one already made for you.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  content!: string;

  @ApiProperty({
    description: 'Full name attached to the content calendar item from the Figma form field #Name.40.',
    example: 'Jane Doe',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  full_name!: string;

  @ApiProperty({
    description: 'Phone number attached to the content calendar item from the Figma megaphone field.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone!: string;

  @ApiPropertyOptional({
    description: 'Optional external link associated with the scheduled content.',
    example: 'https://example.com/posts/austin-q2-market-update',
    nullable: true,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string;
}

export class UpdateContentCalendarEntryDto {
  @ApiPropertyOptional({
    description: 'Updated short title shown for the scheduled content item.',
    example: 'Market update - Austin Q2 revised',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  title?: string;

  @ApiPropertyOptional({
    description: 'Updated scheduled publish date and time in ISO 8601 format.',
    example: '2026-06-16T17:00:00Z',
    format: 'date-time',
  })
  @IsOptional()
  @IsDateString()
  date?: string;

  @ApiPropertyOptional({
    description: 'Updated full content body for the calendar entry.',
    example: 'Updated content strategy tailored for Austin listings and neighborhood insights.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  content?: string;

  @ApiPropertyOptional({
    description: 'Updated display description for the frontend. Defaults to content when omitted.',
    example: 'Updated content strategy tailored for Austin listings and neighborhood insights.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  description?: string;

  @ApiPropertyOptional({
    description: 'Updated full name attached to the content calendar item.',
    example: 'Jane Doe',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  full_name?: string;

  @ApiPropertyOptional({
    description: 'Updated phone number attached to the content calendar item.',
    example: '+1-555-0101',
  })
  @Transform(trimmedString)
  @IsOptional()
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone?: string;

  @ApiPropertyOptional({
    description: 'Updated external link associated with the scheduled content. Send null or empty string to clear it.',
    example: 'https://example.com/posts/austin-q2-market-update-revised',
    nullable: true,
  })
  @Transform(({ value }: { value: unknown }): unknown => {
    if (value === null || value === '') {
      return null;
    }
    return typeof value === 'string' ? value.trim() : value;
  })
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string | null;
}

export class ContentCalendarEntryResponseDto {
  @ApiProperty({ description: 'Unique content calendar entry identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({
    description: 'Short title shown for the scheduled content item.',
    example: 'Market update - Austin Q2',
  })
  title!: string;

  @ApiProperty({
    description: 'Scheduled publish date and time in ISO 8601 format.',
    example: '2026-06-15T00:00:00.000Z',
    format: 'date-time',
  })
  date!: string;

  @ApiProperty({
    description: 'Full content body for the calendar entry.',
    example:
      'Your personal content calendar designed to grow your business - made specifically for you. Drag, drop, edit, and curate your perfect content strategy or feel free to use this one already made for you.',
  })
  content!: string;

  @ApiProperty({
    description: 'Frontend-friendly description field displayed in the content calendar UI.',
    example:
      'Your personal content calendar designed to grow your business - made specifically for you. Drag, drop, edit, and curate your perfect content strategy or feel free to use this one already made for you.',
  })
  description!: string;

  @ApiProperty({ description: 'Full name attached to the content item.', example: 'Jane Doe' })
  full_name!: string;

  @ApiProperty({ description: 'Phone number attached to the content item.', example: '+1-555-0100' })
  phone!: string;

  @ApiPropertyOptional({
    description: 'Optional external link associated with the scheduled content.',
    example: 'https://example.com/posts/austin-q2-market-update',
    nullable: true,
  })
  link!: string | null;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful entries always return null.',
    example: null,
    nullable: true,
    type: Object,
  })
  error!: null;

  @ApiProperty({ description: 'Whether the content entry is active and visible in the calendar.', example: true })
  is_active!: boolean;

  @ApiProperty({
    description: 'Entry creation timestamp in ISO 8601 format.',
    example: '2026-06-01T10:00:00.000Z',
    format: 'date-time',
  })
  created_at!: string;

  @ApiProperty({
    description: 'Entry last update timestamp in ISO 8601 format.',
    example: '2026-06-02T12:30:00.000Z',
    format: 'date-time',
  })
  updated_at!: string;
}

export class ContentCalendarListDataDto {
  @ApiProperty({
    description: 'Active content calendar entries for the authenticated user.',
    type: [ContentCalendarEntryResponseDto],
  })
  items!: ContentCalendarEntryResponseDto[];
}

export class ContentCalendarListResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({
    description: 'UI-safe list outcome message.',
    example: 'Content calendar entries retrieved successfully',
  })
  message!: string;

  @ApiProperty({ type: ContentCalendarListDataDto })
  data!: ContentCalendarListDataDto;
}

export class ContentCalendarCreateResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({
    description: 'UI-safe create outcome message.',
    example: 'Content entry created successfully',
  })
  message!: string;

  @ApiProperty({ type: ContentCalendarEntryResponseDto })
  data!: ContentCalendarEntryResponseDto;
}

export class ContentCalendarUpdateResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({
    description: 'UI-safe update outcome message.',
    example: 'Content entry updated successfully',
  })
  message!: string;

  @ApiProperty({ type: ContentCalendarEntryResponseDto })
  data!: ContentCalendarEntryResponseDto;
}

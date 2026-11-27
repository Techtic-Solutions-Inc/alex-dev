import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform, Type } from 'class-transformer';
import {
  ArrayMaxSize,
  ArrayUnique,
  Equals,
  IsArray,
  IsBoolean,
  IsIn,
  IsInt,
  IsNotEmpty,
  IsOptional,
  IsString,
  IsUrl,
  Matches,
  Max,
  MaxLength,
  Min,
} from 'class-validator';

const trimmedString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);

const trimmedTags = ({ value }: { value: unknown }): unknown => {
  if (!Array.isArray(value)) {
    return value;
  }
  return value
    .map((tag) => (typeof tag === 'string' ? tag.trim() : tag))
    .filter((tag) => typeof tag === 'string' && tag.length > 0);
};

export class CreateRealEstateContentDto {
  @ApiProperty({
    description: 'Content title displayed as the frontend `name` field on the Content List screen.',
    example: 'Hates to see me coming',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  title!: string;

  @ApiProperty({
    description: 'Marketing description shown on the content card.',
    example: 'Trend-ready Instagram caption tailored for local market storytelling.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  description!: string;

  @ApiProperty({
    description: 'Preview image URL for the template.',
    example: 'https://cdn.example.com/templates/hates-to-see-me-coming.jpg',
  })
  @Transform(trimmedString)
  @IsUrl({ require_protocol: true }, { message: 'image_url must be a valid URL' })
  image_url!: string;

  @ApiPropertyOptional({
    description: 'Optional destination link for the template (frontend `link` field).',
    example: 'https://example.com/templates/hates-to-see-me-coming',
    nullable: true,
  })
  @Transform(({ value }) => (value === null || value === undefined ? value : trimmedString({ value })))
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string;

  @ApiPropertyOptional({
    description: 'City placeholder used by localized templates (frontend `city` field).',
    example: 'Austin',
    maxLength: 100,
    nullable: true,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @MaxLength(100)
  city?: string;

  @ApiProperty({
    description: 'Searchable tags for filtering content types.',
    example: ['instagram', 'reel', 'trend'],
    type: [String],
  })
  @Transform(trimmedTags)
  @IsArray()
  @ArrayMaxSize(20)
  @ArrayUnique()
  @IsString({ each: true })
  @IsNotEmpty({ each: true })
  @MaxLength(40, { each: true })
  tags!: string[];

  @ApiProperty({
    description: 'Mobile phone number from the Figma Mobile App Development field.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone!: string;

  @ApiProperty({
    description: 'User must accept the Terms of Use and Privacy Policy before creating content.',
    example: true,
  })
  @IsBoolean()
  @Equals(true, { message: 'You must accept the Terms of Use and Privacy Policy' })
  terms_accepted!: boolean;
}

export class UpdateRealEstateContentDto {
  @ApiPropertyOptional({ description: 'Updated content title.', example: 'Things I consider perfect', maxLength: 160 })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  title?: string;

  @ApiPropertyOptional({
    description: 'Updated description.',
    example: 'Updated localized caption for city-specific campaigns.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  description?: string;

  @ApiPropertyOptional({
    description: 'Updated preview image URL.',
    example: 'https://cdn.example.com/templates/things-perfect.jpg',
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'image_url must be a valid URL' })
  image_url?: string;

  @ApiPropertyOptional({
    description: 'Updated destination link.',
    example: 'https://example.com/templates/things-perfect',
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string;

  @ApiPropertyOptional({ description: 'Updated city label.', example: 'Denver', maxLength: 100 })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @MaxLength(100)
  city?: string;

  @ApiPropertyOptional({ description: 'Updated tags.', example: ['instagram', 'story'], type: [String] })
  @Transform(trimmedTags)
  @IsOptional()
  @IsArray()
  @ArrayMaxSize(20)
  @ArrayUnique()
  @IsString({ each: true })
  @IsNotEmpty({ each: true })
  @MaxLength(40, { each: true })
  tags?: string[];

  @ApiPropertyOptional({ description: 'Updated phone number.', example: '+1-555-0101' })
  @Transform(trimmedString)
  @IsOptional()
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone?: string;
}

export class RealEstateContentListQueryDto {
  @ApiPropertyOptional({
    description: 'Free-text search across title, description, tags, and city. Omit to list all; empty values are rejected.',
    example: 'instagram',
  })
  @IsOptional()
  @IsString()
  search?: string;

  @ApiPropertyOptional({
    description: 'Sort order. `newest` sorts by creation time descending.',
    example: 'newest',
    default: 'newest',
    enum: ['newest', 'oldest'],
  })
  @IsOptional()
  @IsIn(['newest', 'oldest'])
  sort: 'newest' | 'oldest' = 'newest';

  @ApiPropertyOptional({ description: 'Page number (1-based).', example: 1, default: 1 })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(1)
  page = 1;

  @ApiPropertyOptional({ description: 'Items per page (max 100).', example: 20, default: 20 })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(1)
  @Max(100)
  limit = 20;
}

export class RealEstateContentItemResponseDto {
  @ApiProperty({ example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({
    description: 'Frontend `name` field mapped from the stored title.',
    example: 'Hates to see me coming',
  })
  name!: string;

  @ApiProperty({ example: 'Trend-ready Instagram caption tailored for local market storytelling.' })
  description!: string;

  @ApiPropertyOptional({ example: 'Austin', nullable: true })
  city!: string | null;

  @ApiPropertyOptional({ example: 'https://example.com/templates/hates-to-see-me-coming', nullable: true })
  link!: string | null;

  @ApiProperty({ example: 'https://cdn.example.com/templates/hates-to-see-me-coming.jpg' })
  image_url!: string;

  @ApiProperty({ example: ['instagram', 'reel'], type: [String] })
  tags!: string[];

  @ApiProperty({ example: '+1-555-0100' })
  phone!: string;

  @ApiProperty({ description: 'Compatibility field; null on success.', example: null, nullable: true })
  error!: null;

  @ApiProperty({ example: '2026-06-01T10:00:00.000Z' })
  created_at!: string;

  @ApiProperty({ example: '2026-06-02T12:30:00.000Z' })
  updated_at!: string;
}

export class RealEstateContentPaginationDto {
  @ApiProperty({ example: 1 })
  page!: number;

  @ApiProperty({ example: 20 })
  limit!: number;

  @ApiProperty({ example: 42 })
  total!: number;

  @ApiProperty({ example: 3 })
  total_pages!: number;

  @ApiProperty({ example: true })
  has_next!: boolean;

  @ApiProperty({ example: false })
  has_previous!: boolean;
}

export class RealEstateContentListDataDto {
  @ApiProperty({ type: [RealEstateContentItemResponseDto] })
  items!: RealEstateContentItemResponseDto[];

  @ApiProperty({ type: RealEstateContentPaginationDto })
  pagination!: RealEstateContentPaginationDto;
}
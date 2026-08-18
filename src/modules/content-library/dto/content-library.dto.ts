import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform, Type } from 'class-transformer';
import {
  ArrayMaxSize,
  ArrayUnique,
  IsArray,
  IsInt,
  IsNotEmpty,
  IsOptional,
  IsString,
  IsUrl,
  Matches,
  MaxLength,
  Min,
} from 'class-validator';

const trimmedString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);

const trimmedTags = ({ value }: { value: unknown }): unknown => {
  if (!Array.isArray(value)) {
    return value;
  }

  return value.map((tag) => (typeof tag === 'string' ? tag.trim() : tag)).filter((tag) => typeof tag === 'string' && tag.length > 0);
};

export class CreateContentLibraryItemDto {
  @ApiProperty({
    description: 'Frontend-facing title displayed in the content library card and detail screen.',
    example: 'Luxury Listing Social Template',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  title!: string;

  @ApiProperty({
    description: 'Detailed marketing copy or caption description shown in the content library UI.',
    example: 'Editable social post template designed for luxury property launches and premium brand campaigns.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  description!: string;

  @ApiProperty({
    description: 'Absolute image URL used by the frontend content card preview.',
    example: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
  })
  @Transform(trimmedString)
  @IsUrl({ require_protocol: true }, { message: 'image_url must be a valid URL' })
  image_url!: string;

  @ApiProperty({
    description: 'Absolute download or open link for the content item.',
    example: 'https://example.com/content-library/luxury-listing-template',
  })
  @Transform(trimmedString)
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link!: string;

  @ApiProperty({
    description: 'Category label used for grouping and filtering content items.',
    example: 'Social Media',
    maxLength: 120,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(120)
  category!: string;

  @ApiProperty({
    description: 'Searchable tag labels used to improve content discovery.',
    example: ['luxury', 'instagram', 'listing'],
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
    description: 'Full name from the Figma form field #Name.40.',
    example: 'Jane Doe',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  full_name!: string;

  @ApiProperty({
    description: 'Phone number from the Figma megaphone field.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone!: string;
}

export class UpdateContentLibraryItemDto {
  @ApiPropertyOptional({
    description: 'Updated title displayed in the content library UI.',
    example: 'Luxury Listing Social Template v2',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  title?: string;

  @ApiPropertyOptional({
    description: 'Updated detailed description shown on the content detail view.',
    example: 'Updated editable social post template for new luxury developments and premium listing announcements.',
    maxLength: 5000,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(5000)
  description?: string;

  @ApiPropertyOptional({
    description: 'Updated image preview URL for the content item.',
    example: 'https://cdn.example.com/content-library/luxury-listing-template-v2.jpg',
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'image_url must be a valid URL' })
  image_url?: string;

  @ApiPropertyOptional({
    description: 'Updated destination link for the content item.',
    example: 'https://example.com/content-library/luxury-listing-template-v2',
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string;

  @ApiPropertyOptional({
    description: 'Updated category label used by list and search filters.',
    example: 'Email Marketing',
    maxLength: 120,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(120)
  category?: string;

  @ApiPropertyOptional({
    description: 'Updated searchable tag labels.',
    example: ['newsletter', 'seller', 'luxury'],
    type: [String],
  })
  @Transform(trimmedTags)
  @IsOptional()
  @IsArray()
  @ArrayMaxSize(20)
  @ArrayUnique()
  @IsString({ each: true })
  @IsNotEmpty({ each: true })
  @MaxLength(40, { each: true })
  tags?: string[];

  @ApiPropertyOptional({
    description: 'Updated full name from the Figma form field.',
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
    description: 'Updated phone number from the Figma form field.',
    example: '+1-555-0101',
  })
  @Transform(trimmedString)
  @IsOptional()
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone?: string;
}

export class ContentLibrarySearchQueryDto {
  @ApiPropertyOptional({
    description: 'Free-text search term matched against title, description, category, and tags.',
    example: 'luxury',
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

export class ContentLibraryItemResponseDto {
  @ApiProperty({ description: 'Unique content library item identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Content title displayed in the library UI.', example: 'Luxury Listing Social Template' })
  title!: string;

  @ApiProperty({
    description: 'Frontend contract link field used for download/open actions.',
    example: 'https://example.com/content-library/luxury-listing-template',
  })
  link!: string;

  @ApiProperty({
    description: 'Detailed content description shown in list and detail views.',
    example: 'Editable social post template designed for luxury property launches and premium brand campaigns.',
  })
  description!: string;

  @ApiProperty({
    description: 'Frontend contract image field mapped from the stored image URL.',
    example: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
  })
  image!: string;

  @ApiProperty({
    description: 'Original stored image URL value retained for backend consumers.',
    example: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
  })
  image_url!: string;

  @ApiProperty({ description: 'Category label for filtering content items.', example: 'Social Media' })
  category!: string;

  @ApiProperty({ description: 'Searchable tag labels.', example: ['luxury', 'instagram', 'listing'], type: [String] })
  tags!: string[];

  @ApiProperty({ description: 'Full name attached to the content item.', example: 'Jane Doe' })
  full_name!: string;

  @ApiProperty({ description: 'Phone number attached to the content item.', example: '+1-555-0100' })
  phone!: string;

  @ApiPropertyOptional({
    description: 'Frontend compatibility field. Successful items always return null.',
    example: null,
    nullable: true,
  })
  error!: null;

  @ApiProperty({ description: 'Whether the content item is active and visible.', example: true })
  is_active!: boolean;

  @ApiProperty({ description: 'Creation timestamp in ISO 8601 format.', example: '2026-06-01T10:00:00.000Z' })
  created_at!: string;

  @ApiProperty({ description: 'Last update timestamp in ISO 8601 format.', example: '2026-06-02T12:30:00.000Z' })
  updated_at!: string;
}

export class ContentLibraryPaginationDto {
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

export class ContentLibraryListDataDto {
  @ApiProperty({ type: [ContentLibraryItemResponseDto] })
  items!: ContentLibraryItemResponseDto[];

  @ApiProperty({ type: ContentLibraryPaginationDto })
  pagination!: ContentLibraryPaginationDto;
}

export class ContentLibraryListResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Content library items retrieved successfully' })
  message!: string;

  @ApiProperty({ type: ContentLibraryListDataDto })
  data!: ContentLibraryListDataDto;
}

export class ContentLibraryCreateResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Content library item created successfully' })
  message!: string;

  @ApiProperty({ type: ContentLibraryItemResponseDto })
  data!: ContentLibraryItemResponseDto;
}

export class ContentLibraryUpdateResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'Content library item updated successfully' })
  message!: string;

  @ApiProperty({ type: ContentLibraryItemResponseDto })
  data!: ContentLibraryItemResponseDto;
}

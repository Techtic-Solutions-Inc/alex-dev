import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform, Type } from 'class-transformer';
import {
  Equals,
  IsBoolean,
  IsEmail,
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

export class BlogMetadataDto {
  @ApiProperty({ example: '2026-01-01T00:00:00.000Z' })
  created_at!: string;

  @ApiProperty({ example: '2026-01-01T00:00:00.000Z' })
  updated_at!: string;
}

export class CreateBlogPostDto {
  @ApiProperty({
    description: 'Blog post title shown on the Blog screen and detail view.',
    example: 'Hates to see me coming',
    maxLength: 200,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty({ message: 'title must not be empty' })
  @MaxLength(200)
  title!: string;

  @ApiProperty({
    description: 'Author contact email displayed on the blog detail screen.',
    example: 'hello@agentwisemarketing.com',
  })
  @Transform(({ value }) => (typeof value === 'string' ? value.trim().toLowerCase() : value))
  @IsEmail({}, { message: 'author_email must be a valid email address' })
  author_email!: string;

  @ApiProperty({
    description: 'Full blog body content.',
    example: 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.',
    maxLength: 100000,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(100000)
  content!: string;

  @ApiProperty({
    description: 'Short preview description for blog list cards.',
    example: 'Insights on local market positioning and social storytelling.',
    maxLength: 2000,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(2000)
  description!: string;

  @ApiPropertyOptional({
    description: 'Optional detail-page link (frontend `link` field).',
    example: 'https://example.com/blog/hates-to-see-me-coming',
    nullable: true,
  })
  @Transform(({ value }) => (value === null || value === undefined ? value : trimmedString({ value })))
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string;

  @ApiProperty({
    description: 'Preview image URL for the blog card.',
    example: 'https://cdn.example.com/blog/hates-to-see-me-coming.jpg',
  })
  @Transform(trimmedString)
  @IsUrl({ require_protocol: true }, { message: 'image_url must be a valid URL' })
  image_url!: string;

  @ApiProperty({
    description: 'Mobile phone from the Figma Mobile App Development field.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone!: string;

  @ApiProperty({
    description: 'User must accept the Terms of Use and Privacy Policy before creating a blog post.',
    example: true,
  })
  @IsBoolean()
  @Equals(true, { message: 'You must accept the Terms of Use and Privacy Policy' })
  terms_accepted!: boolean;
}

export class UpdateBlogPostDto {
  @ApiPropertyOptional({ description: 'Updated blog title.', example: 'Updated market insights', maxLength: 200 })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty({ message: 'title must not be empty' })
  @MaxLength(200)
  title?: string;

  @ApiPropertyOptional({ description: 'Updated author email.', example: 'author@example.com' })
  @Transform(({ value }) => (typeof value === 'string' ? value.trim().toLowerCase() : value))
  @IsOptional()
  @IsEmail({}, { message: 'author_email must be a valid email address' })
  author_email?: string;

  @ApiPropertyOptional({ description: 'Updated blog body.', maxLength: 100000 })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(100000)
  content?: string;

  @ApiPropertyOptional({ description: 'Updated card description.', maxLength: 2000 })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(2000)
  description?: string;

  @ApiPropertyOptional({ description: 'Updated destination link.' })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'link must be a valid URL' })
  link?: string;

  @ApiPropertyOptional({ description: 'Updated preview image URL.' })
  @Transform(trimmedString)
  @IsOptional()
  @IsUrl({ require_protocol: true }, { message: 'image_url must be a valid URL' })
  image_url?: string;

  @ApiPropertyOptional({ description: 'Updated phone number.', example: '+1-555-0101' })
  @Transform(trimmedString)
  @IsOptional()
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone?: string;
}

export class BlogListQueryDto {
  @ApiPropertyOptional({
    description: 'Free-text search across title, description, and content. Empty values return 400.',
    example: 'market',
  })
  @IsOptional()
  @IsString()
  search?: string;

  @ApiPropertyOptional({
    description: 'Sort order for blog posts.',
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

export class BlogPostListItemDto {
  @ApiProperty({ example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ example: 'Hates to see me coming' })
  title!: string;

  @ApiProperty({ example: 'Insights on local market positioning and social storytelling.' })
  description!: string;

  @ApiProperty({ example: 'hello@agentwisemarketing.com' })
  author_email!: string;

  @ApiPropertyOptional({ example: 'https://example.com/blog/hates-to-see-me-coming', nullable: true })
  link!: string | null;

  @ApiProperty({ example: 'https://cdn.example.com/blog/hates-to-see-me-coming.jpg' })
  image_url!: string;

  @ApiProperty({ example: '+1-555-0100' })
  phone!: string;

  @ApiProperty({ description: 'Compatibility field; null on success.', example: null, nullable: true })
  error!: null;

  @ApiProperty({ type: BlogMetadataDto })
  metadata!: BlogMetadataDto;
}

export class BlogPostDetailDto {
  @ApiProperty({ example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ example: 'Hates to see me coming' })
  title!: string;

  @ApiProperty({ example: 'hello@agentwisemarketing.com' })
  author_email!: string;

  @ApiProperty({
    example: 'Lorem Ipsum is simply dummy text of the printing and typesetting industry.',
  })
  content!: string;

  @ApiProperty({ example: 'Insights on local market positioning and social storytelling.' })
  description!: string;

  @ApiPropertyOptional({ example: 'https://example.com/blog/hates-to-see-me-coming', nullable: true })
  link!: string | null;

  @ApiProperty({ example: '+1-555-0100' })
  phone!: string;

  @ApiProperty({ example: true })
  terms_accepted!: boolean;

  @ApiProperty({ type: BlogMetadataDto })
  metadata!: BlogMetadataDto;

  @ApiProperty({ description: 'Compatibility field; null on success.', example: null, nullable: true })
  error!: null;
}

export class BlogPaginationDto {
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

export class BlogListDataDto {
  @ApiProperty({ type: [BlogPostListItemDto] })
  items!: BlogPostListItemDto[];

  @ApiProperty({ type: BlogPaginationDto })
  pagination!: BlogPaginationDto;

  @ApiProperty({
    description: 'Blog screen: primary identifier mirrored from the first item (null when empty).',
    nullable: true,
  })
  id!: string | null;

  @ApiProperty({ description: 'Mirrored title from the first list item.', nullable: true })
  title!: string | null;

  @ApiProperty({ description: 'Mirrored description from the first list item.', nullable: true })
  description!: string | null;

  @ApiProperty({ description: 'Mirrored link from the first list item.', nullable: true })
  link!: string | null;

  @ApiProperty({ description: 'Compatibility error slot; null on success.', example: null, nullable: true })
  error!: null;
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform, Type } from 'class-transformer';
import { IsInt, IsNotEmpty, IsOptional, IsString, Matches, MaxLength, Min } from 'class-validator';

const trimmedString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);

export class ContentLibraryDedicatedSearchQueryDto {
  @ApiProperty({
    description:
      'Keyword used to search active content library items across title, description, category, tags, full name, and phone.',
    example: 'luxury',
    maxLength: 120,
  })
  @Transform(trimmedString)
  @IsString()
  @IsNotEmpty({ message: 'Search query cannot be empty' })
  @MaxLength(120)
  query!: string;

  @ApiPropertyOptional({
    description: 'Optional filter matching the Figma #Name.40 field on content items.',
    example: 'Jane Doe',
    maxLength: 160,
  })
  @Transform(trimmedString)
  @IsOptional()
  @IsString()
  @MaxLength(160)
  full_name?: string;

  @ApiPropertyOptional({
    description: 'Optional filter matching the Figma phone field on content items.',
    example: '+1-555-0100',
  })
  @Transform(trimmedString)
  @IsOptional()
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone?: string;

  @ApiPropertyOptional({
    description: 'Page number for paginated search results.',
    example: 1,
    default: 1,
  })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(1)
  page?: number;

  @ApiPropertyOptional({
    description: 'Maximum number of search results per page (max 100).',
    example: 20,
    default: 20,
  })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(1)
  limit?: number;
}
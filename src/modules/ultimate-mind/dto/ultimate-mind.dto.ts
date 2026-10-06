import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';
import { Transform, Type } from 'class-transformer';
import { IsInt, IsMongoId, IsNotEmpty, IsOptional, IsString, Matches, MaxLength, Min } from 'class-validator';

const PHONE_REGEX = /^\+?[0-9][0-9\s\-().]{6,24}$/;

const trimString = ({ value }: { value: unknown }): unknown => (typeof value === 'string' ? value.trim() : value);

export class CreateUltimateMindAiCreditDto {
  @ApiProperty({
    description: 'MongoDB ObjectId of the user this AI credit record belongs to.',
    example: '66df0b7814b3e891e4ebcd21',
  })
  @IsMongoId({ message: 'user_id must be a valid MongoDB ObjectId' })
  user_id!: string;

  @ApiProperty({
    description: 'Current AI credit usage count for the linked user.',
    example: 1420,
    minimum: 0,
  })
  @Type(() => Number)
  @IsInt()
  @Min(0)
  usage!: number;

  @ApiProperty({
    description: 'Maximum AI credit limit allocated to the linked user.',
    example: 5000,
    minimum: 1,
  })
  @Type(() => Number)
  @IsInt()
  @Min(1)
  limit!: number;

  @ApiProperty({
    description: 'Full name from the Figma form field #Name.40.',
    example: 'Jane Doe',
    maxLength: 160,
  })
  @Transform(trimString)
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  full_name!: string;

  @ApiProperty({
    description: 'Phone number from the Figma megaphone field.',
    example: '+1-555-0100',
  })
  @Transform(trimString)
  @Matches(PHONE_REGEX, { message: 'phone must be a valid phone number' })
  phone!: string;
}

export class UpdateUltimateMindAiCreditDto {
  @ApiPropertyOptional({
    description: 'Updated AI credit usage count.',
    example: 1500,
    minimum: 0,
  })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(0)
  usage?: number;

  @ApiPropertyOptional({
    description: 'Updated AI credit limit.',
    example: 6000,
    minimum: 1,
  })
  @Type(() => Number)
  @IsOptional()
  @IsInt()
  @Min(1)
  limit?: number;

  @ApiPropertyOptional({
    description: 'Updated full name from the Figma form field #Name.40.',
    example: 'Jane Doe',
    maxLength: 160,
  })
  @Transform(trimString)
  @IsOptional()
  @IsString()
  @IsNotEmpty()
  @MaxLength(160)
  full_name?: string;

  @ApiPropertyOptional({
    description: 'Updated phone number from the Figma megaphone field.',
    example: '+1-555-0101',
  })
  @Transform(trimString)
  @IsOptional()
  @Matches(PHONE_REGEX, { message: 'phone must be a valid phone number' })
  phone?: string;
}

export class AiCreditUsageItemDto {
  @ApiProperty({ description: 'Unique AI credit usage record identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Display name of the linked user.', example: 'Joseph Stanley' })
  user!: string;

  @ApiProperty({ description: 'Current AI credit usage for the linked user.', example: 1420 })
  usage!: number;

  @ApiProperty({ description: 'Maximum AI credit limit for the linked user.', example: 5000 })
  limit!: number;
}

export class UltimateMindAiCreditListDataDto {
  @ApiProperty({ type: [AiCreditUsageItemDto] })
  ai_credit_usage!: AiCreditUsageItemDto[];

  @ApiProperty({ description: 'Full name of the authenticated user viewing the Ultimate Mind screen.', example: 'Jane Doe' })
  full_name!: string;

  @ApiPropertyOptional({
    description: 'Phone number of the authenticated user viewing the Ultimate Mind screen.',
    example: '+1-555-0100',
    nullable: true,
  })
  phone!: string | null;
}

export class UltimateMindAiCreditRecordDataDto extends AiCreditUsageItemDto {
  @ApiProperty({ description: 'Full name stored on the AI credit record.', example: 'Jane Doe' })
  full_name!: string;

  @ApiProperty({ description: 'Phone number stored on the AI credit record.', example: '+1-555-0100' })
  phone!: string;
}

export class UltimateMindAiCreditListResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'AI credit usage records retrieved successfully' })
  message!: string;

  @ApiProperty({ type: UltimateMindAiCreditListDataDto })
  data!: UltimateMindAiCreditListDataDto;
}

export class UltimateMindAiCreditCreateResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'AI credit usage record created successfully' })
  message!: string;

  @ApiProperty({ type: UltimateMindAiCreditRecordDataDto })
  data!: UltimateMindAiCreditRecordDataDto;
}

export class UltimateMindAiCreditUpdateResponseDto {
  @ApiProperty({ example: true })
  success!: true;

  @ApiProperty({ example: 'AI credit usage record updated successfully' })
  message!: string;

  @ApiProperty({ type: UltimateMindAiCreditRecordDataDto })
  data!: UltimateMindAiCreditRecordDataDto;
}

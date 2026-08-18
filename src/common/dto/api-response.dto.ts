import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class ApiErrorDto {
  @ApiProperty({ description: 'Stable machine-readable error code', example: 'VALIDATION_ERROR' })
  code!: string;

  @ApiPropertyOptional({
    description: 'Optional field-level validation details',
    example: { email: ['email must be an email'] },
    nullable: true,
  })
  details!: Record<string, string[]> | null;
}

export class ApiErrorResponseDto {
  @ApiProperty({ example: false })
  success!: false;

  @ApiProperty({ description: 'Safe message suitable for display in the UI', example: 'Validation failed' })
  message!: string;

  @ApiProperty({ type: ApiErrorDto })
  error!: ApiErrorDto;

  @ApiProperty({
    description: 'Request path that produced the error.',
    example: '/api/auth/signup',
  })
  path!: string;

  @ApiProperty({
    description: 'ISO 8601 timestamp at which the error response was created.',
    example: '2026-08-17T07:52:00.000Z',
    format: 'date-time',
  })
  timestamp!: string;
}

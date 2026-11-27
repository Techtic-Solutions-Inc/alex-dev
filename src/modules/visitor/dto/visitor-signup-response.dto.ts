import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class VisitorSignupUserDto {
  @ApiProperty({ example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ example: 'John Doe' })
  name!: string;

  @ApiProperty({ example: 'John Doe' })
  full_name!: string;

  @ApiProperty({ example: 'John' })
  first_name!: string;

  @ApiProperty({ example: 'Doe' })
  last_name!: string;

  @ApiProperty({ example: 'john.doe@example.com' })
  email!: string;

  @ApiPropertyOptional({ example: '+1-555-0100', nullable: true })
  phone!: string | null;

  @ApiProperty({ example: false })
  email_verified!: boolean;

  @ApiProperty({
    description: 'UI helper copy for the Sign Up success state.',
    example: 'Please check your email to verify your address before signing in.',
    nullable: true,
  })
  description!: string | null;

  @ApiProperty({
    description: 'Link to the Sign In screen for returning users.',
    example: '/sign-in',
    nullable: true,
  })
  link!: string | null;

  @ApiPropertyOptional({
    description: 'Compatibility error slot; null on success.',
    type: String,
    nullable: true,
    example: null,
  })
  error?: string | null;
}

export class VisitorSignupResponseDto {
  @ApiProperty({ example: true })
  success!: boolean;

  @ApiProperty({ example: 'Account created. Please check your email to verify your address.' })
  message!: string;

  @ApiProperty({ type: VisitorSignupUserDto })
  data!: VisitorSignupUserDto;
}

import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class RegisteredUserResponseDto {
  @ApiProperty({ description: 'Public user identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Display name assembled from first and last name.', example: 'John Doe' })
  name!: string;

  @ApiProperty({ description: 'User given name.', example: 'John' })
  first_name!: string;

  @ApiProperty({ description: 'User family name.', example: 'Doe' })
  last_name!: string;

  @ApiProperty({ description: 'Verified email address.', example: 'john.doe@example.com' })
  email!: string;

  @ApiProperty({ description: 'Whether the email verification link has been consumed.', example: false })
  email_verified!: boolean;
}

export class SignupResponseDto {
  @ApiProperty({ description: 'Indicates the request completed successfully.', example: true })
  success!: true;

  @ApiProperty({
    description: 'UI-safe sign-up outcome message.',
    example: 'Account created. Please check your email to verify your address.',
  })
  message!: string;

  @ApiProperty({ type: RegisteredUserResponseDto })
  data!: RegisteredUserResponseDto;
}

export class VerifyEmailResponseDto extends SignupResponseDto {
  @ApiProperty({
    description: 'Verified user profile without secrets.',
    type: RegisteredUserResponseDto,
    example: {
      id: '66df0b7814b3e891e4ebcd21',
      name: 'John Doe',
      first_name: 'John',
      last_name: 'Doe',
      email: 'john.doe@example.com',
      email_verified: true,
    },
  })
  declare data: RegisteredUserResponseDto;
}

export class LoginUserResponseDto {
  @ApiProperty({ description: 'Public user identifier.', example: '66df0b7814b3e891e4ebcd21' })
  id!: string;

  @ApiProperty({ description: 'Email address used to sign in.', example: 'john.doe@example.com' })
  email!: string;
}

export class LoginResponseDataDto extends LoginUserResponseDto {
  @ApiProperty({
    description: 'JWT access token for use in the Authorization bearer header.',
    example: 'eyJhbGciOiJIUzI1NiJ9.access-token',
  })
  token!: string;

  @ApiProperty({
    description: 'JWT access token, retained for compatibility with token refresh responses.',
    example: 'eyJhbGciOiJIUzI1NiJ9.access-token',
  })
  accessToken!: string;

  @ApiPropertyOptional({
    description:
      'JWT refresh token used to obtain a new access token. Auth0 returns this only when the client is authorized for offline access.',
    example: 'eyJhbGciOiJIUzI1NiJ9.refresh-token',
  })
  refreshToken?: string;

  @ApiProperty({ description: 'Authentication scheme for the access token.', example: 'Bearer' })
  tokenType!: 'Bearer';
}

export class LoginResponseDto {
  @ApiProperty({ description: 'Indicates the request completed successfully.', example: true })
  success!: true;

  @ApiProperty({ description: 'UI-safe sign-in outcome message.', example: 'Signed in successfully' })
  message!: string;

  @ApiProperty({
    description: 'Authenticated user and issued token pair. Passwords are never returned.',
    example: {
      id: '66df0b7814b3e891e4ebcd21',
      email: 'john.doe@example.com',
      token: 'eyJhbGciOiJIUzI1NiJ9.access-token',
      accessToken: 'eyJhbGciOiJIUzI1NiJ9.access-token',
      refreshToken: 'eyJhbGciOiJIUzI1NiJ9.refresh-token',
      tokenType: 'Bearer',
    },
  })
  data!: LoginResponseDataDto;
}

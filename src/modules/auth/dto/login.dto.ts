import { ApiProperty } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { IsEmail, IsString, Length, Matches } from 'class-validator';

export class LoginDto {
  @ApiProperty({
    description: 'Email address associated with the user account.',
    example: 'john.doe@example.com',
    format: 'email',
    maxLength: 254,
  })
  @Transform(({ value }: { value: unknown }) => (typeof value === 'string' ? value.trim().toLowerCase() : value))
  @IsEmail({}, { message: 'email must be a valid email address' })
  @Length(1, 254, { message: 'email must be at most 254 characters' })
  email!: string;

  @ApiProperty({
    description:
      'Account password. It must have at least eight characters, including uppercase, lowercase, and numeric characters.',
    example: 'Password123',
    format: 'password',
    minLength: 8,
    writeOnly: true,
  })
  @IsString({ message: 'password must be a string' })
  @Matches(/^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$/, {
    message: 'password must be at least 8 characters and include an uppercase letter, lowercase letter, and number',
  })
  password!: string;
}

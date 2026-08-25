import { ApiProperty } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { Equals, IsBoolean, IsEmail, IsNotEmpty, IsOptional, IsString, Length, Matches } from 'class-validator';

export class SignupDto {
  @ApiProperty({
    description: 'User given name.',
    example: 'John',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(({ value }: { value: unknown }) => (typeof value === 'string' ? value.trim() : value))
  @IsString({ message: 'first_name must be a string' })
  @IsNotEmpty({ message: 'first_name is required' })
  @Length(1, 100, { message: 'first_name must be between 1 and 100 characters' })
  first_name!: string;

  @ApiProperty({
    description: 'User family name.',
    example: 'Doe',
    minLength: 1,
    maxLength: 100,
  })
  @Transform(({ value }: { value: unknown }) => (typeof value === 'string' ? value.trim() : value))
  @IsString({ message: 'last_name must be a string' })
  @IsNotEmpty({ message: 'last_name is required' })
  @Length(1, 100, { message: 'last_name must be between 1 and 100 characters' })
  last_name!: string;

  @ApiProperty({
    description: 'Unique email address used for account verification and sign-in.',
    example: 'john.doe@example.com',
    format: 'email',
  })
  @Transform(({ value }: { value: unknown }) => (typeof value === 'string' ? value.trim().toLowerCase() : value))
  @IsEmail({}, { message: 'email must be a valid email address' })
  @Length(1, 254, { message: 'email must be at most 254 characters' })
  email!: string;

  @ApiProperty({
    description: 'Optional phone number used by dashboard and profile experiences.',
    example: '+1-555-0100',
    required: false,
  })
  @Transform(({ value }: { value: unknown }) => (typeof value === 'string' ? value.trim() : value))
  @IsOptional()
  @Matches(/^\+?[0-9][0-9\s\-().]{6,24}$/, { message: 'phone must be a valid phone number' })
  phone?: string;

  @ApiProperty({
    description:
      'Account password. Must contain at least eight characters, one uppercase letter, one number, and one special character.',
    example: 'StrongPassword123!',
    format: 'password',
    minLength: 8,
    writeOnly: true,
  })
  @IsString({ message: 'password must be a string' })
  @Matches(/^(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$/, {
    message: 'password must be at least 8 characters and include an uppercase letter, number, and special character',
  })
  password!: string;

  @ApiProperty({
    description: 'Must be true to confirm acceptance of the Terms of Use and Privacy Policy.',
    example: true,
  })
  @IsBoolean({ message: 'terms_accepted must be a boolean' })
  @Equals(true, { message: 'terms_accepted must be true' })
  terms_accepted!: boolean;
}

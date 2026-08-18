import { ApiProperty } from '@nestjs/swagger';
import { Transform } from 'class-transformer';
import { IsNotEmpty, IsString, Matches } from 'class-validator';

export class VerifyEmailDto {
  @ApiProperty({
    description: 'Single-use email-verification token received in the verification email.',
    example: 'd1c8cd59e2d843cc94a9b8c96a1b4502f5402af9c43a45b98df2c3f2e11ae483',
  })
  @Transform(({ value }: { value: unknown }) => (typeof value === 'string' ? value.trim() : value))
  @IsString({ message: 'token must be a string' })
  @IsNotEmpty({ message: 'token is required' })
  @Matches(/^[a-f0-9]{64}$/, {
    message: 'token is invalid',
  })
  token!: string;
}

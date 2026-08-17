import { ApiProperty } from '@nestjs/swagger';
import { IsJWT, IsNotEmpty } from 'class-validator';

export class RefreshTokenDto {
  @ApiProperty({
    description: 'Valid refresh JWT previously issued by the API.',
    example: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyJ9.signature',
  })
  @IsJWT({ message: 'refreshToken must be a valid JWT' })
  @IsNotEmpty({ message: 'refreshToken is required' })
  refreshToken!: string;
}

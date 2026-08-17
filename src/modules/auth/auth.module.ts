import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { MongooseModule } from '@nestjs/mongoose';
import { Auth0AuthenticationService } from './auth0-authentication.service';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { EmailVerificationService } from './email-verification.service';
import { User, UserSchema } from './entities/user.schema';

@Module({
  imports: [
    MongooseModule.forFeature([{ name: User.name, schema: UserSchema }]),
    JwtModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        secret: configService.getOrThrow<string>('JWT_SECRET'),
      }),
    }),
  ],
  controllers: [AuthController],
  providers: [AuthService, Auth0AuthenticationService, EmailVerificationService],
  exports: [JwtModule, AuthService],
})
export class AuthModule {}

import { Module } from '@nestjs/common';
import { ConfigModule, ConfigService } from '@nestjs/config';
import { JwtModule } from '@nestjs/jwt';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { Auth0AuthenticationService } from './auth0-authentication.service';
import { AuthController } from './auth.controller';
import { AuthService } from './auth.service';
import { EmailVerificationService } from './email-verification.service';
import { RevokedAccessToken, RevokedAccessTokenSchema } from './entities/revoked-access-token.schema';
import { User, UserSchema } from './entities/user.schema';
import { SessionRevocationService } from './session-revocation.service';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: User.name, schema: UserSchema },
      { name: RevokedAccessToken.name, schema: RevokedAccessTokenSchema },
    ]),
    JwtModule.registerAsync({
      imports: [ConfigModule],
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        secret: configService.getOrThrow<string>('JWT_SECRET'),
      }),
    }),
  ],
  controllers: [AuthController],
  providers: [AuthService, Auth0AuthenticationService, EmailVerificationService, SessionRevocationService, JwtAuthGuard],
  exports: [JwtModule, AuthService, Auth0AuthenticationService, SessionRevocationService, JwtAuthGuard],
})
export class AuthModule {}
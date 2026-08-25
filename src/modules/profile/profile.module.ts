import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { AuthModule } from '../auth/auth.module';
import { User, UserSchema } from '../auth/entities/user.schema';
import { ProfileController } from './profile.controller';
import { ProfileContent, ProfileContentSchema } from './entities/profile-content.schema';
import { ProfileDownload, ProfileDownloadSchema } from './entities/profile-download.schema';
import { ProfileContentAnalyticsService } from './profile-content-analytics.service';
import { ProfileService } from './profile.service';

@Module({
  imports: [
    AuthModule,
    MongooseModule.forFeature([
      { name: User.name, schema: UserSchema },
      { name: ProfileContent.name, schema: ProfileContentSchema },
      { name: ProfileDownload.name, schema: ProfileDownloadSchema },
    ]),
  ],
  controllers: [ProfileController],
  providers: [ProfileService, ProfileContentAnalyticsService, JwtAuthGuard],
})
export class ProfileModule {}

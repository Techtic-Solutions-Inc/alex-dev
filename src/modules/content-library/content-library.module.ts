import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { AuthModule } from '../auth/auth.module';
import { User, UserSchema } from '../auth/entities/user.schema';
import { ContentLibraryAnalyticsService } from './content-library-analytics.service';
import { ContentLibraryController } from './content-library.controller';
import { ContentLibraryService } from './content-library.service';
import { ContentLibraryItem, ContentLibraryItemSchema } from './entities/content-library-item.schema';

@Module({
  imports: [
    AuthModule,
    MongooseModule.forFeature([
      { name: User.name, schema: UserSchema },
      { name: ContentLibraryItem.name, schema: ContentLibraryItemSchema },
    ]),
  ],
  controllers: [ContentLibraryController],
  providers: [ContentLibraryService, ContentLibraryAnalyticsService, JwtAuthGuard, RolesGuard],
  exports: [ContentLibraryService],
})
export class ContentLibraryModule {}

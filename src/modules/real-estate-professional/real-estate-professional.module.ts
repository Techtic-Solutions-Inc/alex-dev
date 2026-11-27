import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { RolesGuard } from '../../common/guards/roles.guard';
import { AuthModule } from '../auth/auth.module';
import { RealEstateProfessionalAuthController } from './auth/real-estate-professional-auth.controller';
import { User, UserSchema } from '../auth/entities/user.schema';
import { RealEstateProfessionalBlogController } from './blog/blog.controller';
import { BlogDetailAccessGuard } from './blog/blog-detail.guard';
import { RealEstateProfessionalBlogService } from './blog/blog.service';
import { RealEstateBlogPost, RealEstateBlogPostSchema } from './blog/entities/blog-post.schema';
import { RealEstateProfessionalContentController } from './content/content.controller';
import { RealEstateProfessionalContentService } from './content/content.service';
import { RealEstateContentItem, RealEstateContentItemSchema } from './content/entities/content-item.schema';

@Module({
  imports: [
    AuthModule,
    MongooseModule.forFeature([
      { name: User.name, schema: UserSchema },
      { name: RealEstateContentItem.name, schema: RealEstateContentItemSchema },
      { name: RealEstateBlogPost.name, schema: RealEstateBlogPostSchema },
    ]),
  ],
  controllers: [
    RealEstateProfessionalAuthController,
    RealEstateProfessionalContentController,
    RealEstateProfessionalBlogController,
  ],
  providers: [RealEstateProfessionalContentService, RealEstateProfessionalBlogService, RolesGuard, BlogDetailAccessGuard],
})
export class RealEstateProfessionalModule {}

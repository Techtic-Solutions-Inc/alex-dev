import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { RolesGuard } from '../../common/guards/roles.guard';
import { AuthModule } from '../auth/auth.module';
import { User, UserSchema } from '../auth/entities/user.schema';
import { RealEstateProfessionalContentController } from './content/content.controller';
import { RealEstateProfessionalContentService } from './content/content.service';
import { RealEstateContentItem, RealEstateContentItemSchema } from './content/entities/content-item.schema';

@Module({
  imports: [
    AuthModule,
    MongooseModule.forFeature([
      { name: User.name, schema: UserSchema },
      { name: RealEstateContentItem.name, schema: RealEstateContentItemSchema },
    ]),
  ],
  controllers: [RealEstateProfessionalContentController],
  providers: [RealEstateProfessionalContentService, JwtAuthGuard, RolesGuard],
})
export class RealEstateProfessionalModule {}

import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { AuthModule } from '../auth/auth.module';
import { CalendarModule } from '../calendar/calendar.module';
import { UltimateMindModule } from '../ultimate-mind/ultimate-mind.module';
import { User, UserSchema } from '../auth/entities/user.schema';
import { DashboardController } from './dashboard.controller';
import { DashboardService } from './dashboard.service';
import { DashboardAnnouncement, DashboardAnnouncementSchema } from './entities/dashboard-announcement.schema';
import { DashboardAnalyticsService } from './dashboard-analytics.service';

@Module({
  imports: [
    AuthModule,
    CalendarModule,
    UltimateMindModule,
    MongooseModule.forFeature([
      { name: DashboardAnnouncement.name, schema: DashboardAnnouncementSchema },
      { name: User.name, schema: UserSchema },
    ]),
  ],
  controllers: [DashboardController],
  providers: [DashboardService, DashboardAnalyticsService, JwtAuthGuard],
})
export class DashboardModule {}

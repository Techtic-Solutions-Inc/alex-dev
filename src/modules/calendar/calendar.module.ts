import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { AuthModule } from '../auth/auth.module';
import { User, UserSchema } from '../auth/entities/user.schema';
import { CalendarAnalyticsService } from './calendar-analytics.service';
import { CalendarController } from './calendar.controller';
import { CalendarService } from './calendar.service';
import { ContentCalendarEntry, ContentCalendarEntrySchema } from './entities/content-calendar-entry.schema';

@Module({
  imports: [
    AuthModule,
    MongooseModule.forFeature([
      { name: ContentCalendarEntry.name, schema: ContentCalendarEntrySchema },
      { name: User.name, schema: UserSchema },
    ]),
  ],
  controllers: [CalendarController],
  providers: [CalendarService, CalendarAnalyticsService, JwtAuthGuard],
  exports: [CalendarService],
})
export class CalendarModule {}

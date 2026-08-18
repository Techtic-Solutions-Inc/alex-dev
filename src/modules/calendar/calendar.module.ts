import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { JwtAuthGuard } from '../../common/guards/jwt.guard';
import { AuthModule } from '../auth/auth.module';
import { CalendarAnalyticsService } from './calendar-analytics.service';
import { CalendarController } from './calendar.controller';
import { CalendarService } from './calendar.service';
import { ContentCalendarEntry, ContentCalendarEntrySchema } from './entities/content-calendar-entry.schema';

@Module({
  imports: [
    AuthModule,
    MongooseModule.forFeature([{ name: ContentCalendarEntry.name, schema: ContentCalendarEntrySchema }]),
  ],
  controllers: [CalendarController],
  providers: [CalendarService, CalendarAnalyticsService, JwtAuthGuard],
  exports: [CalendarService],
})
export class CalendarModule {}

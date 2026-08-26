import { Module } from '@nestjs/common';
import { MongooseModule } from '@nestjs/mongoose';
import { GoogleAnalyticsClient } from '../../common/analytics/google-analytics.client';
import { VisitorHomeContent, VisitorHomeContentSchema } from './entities/visitor-home-content.schema';
import { VisitorHomeSubscription, VisitorHomeSubscriptionSchema } from './entities/visitor-home-subscription.schema';
import { VisitorHomeAnalyticsService } from './visitor-home-analytics.service';
import { VisitorHomeController } from './visitor-home.controller';
import { VisitorHomeService } from './visitor-home.service';

@Module({
  imports: [
    MongooseModule.forFeature([
      { name: VisitorHomeContent.name, schema: VisitorHomeContentSchema },
      { name: VisitorHomeSubscription.name, schema: VisitorHomeSubscriptionSchema },
    ]),
  ],
  controllers: [VisitorHomeController],
  providers: [VisitorHomeService, VisitorHomeAnalyticsService, GoogleAnalyticsClient],
  exports: [VisitorHomeService],
})
export class VisitorModule {}

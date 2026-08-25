import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

type DashboardAnalyticsEvent =
  | 'dashboard_viewed'
  | 'dashboard_announcements_viewed'
  | 'dashboard_announcement_created'
  | 'dashboard_analytics_viewed'
  | 'dashboard_question_asked';

@Injectable()
export class DashboardAnalyticsService {
  private readonly logger = new Logger(DashboardAnalyticsService.name);

  constructor(private readonly configService: ConfigService) {}

  async trackEvent(
    userId: string,
    eventName: DashboardAnalyticsEvent,
    metadata: Record<string, string | number | boolean | null> = {},
  ): Promise<void> {
    const measurementId = this.configService.get<string>('GOOGLE_ANALYTICS_MEASUREMENT_ID');
    const apiSecret = this.configService.get<string>('GOOGLE_ANALYTICS_API_SECRET');

    if (!measurementId || !apiSecret) {
      return;
    }

    try {
      const response = await fetch(
        `https://www.google-analytics.com/mp/collect?measurement_id=${encodeURIComponent(measurementId)}&api_secret=${encodeURIComponent(apiSecret)}`,
        {
          method: 'POST',
          headers: { 'content-type': 'application/json' },
          body: JSON.stringify({
            client_id: userId,
            user_id: userId,
            events: [
              {
                name: eventName,
                params: {
                  feature: 'dashboard',
                  ...metadata,
                },
              },
            ],
          }),
        },
      );

      if (!response.ok) {
        this.logger.warn(`Google Analytics tracking failed with status ${response.status} for event ${eventName}`);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Unknown analytics tracking failure';
      this.logger.warn(`Google Analytics tracking failed for event ${eventName}: ${message}`);
    }
  }
}

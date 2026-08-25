import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

type CalendarAnalyticsEvent =
  'content_calendar_viewed' | 'content_calendar_created' | 'content_calendar_updated' | 'content_calendar_deleted';

@Injectable()
export class CalendarAnalyticsService {
  private readonly logger = new Logger(CalendarAnalyticsService.name);

  constructor(private readonly configService: ConfigService) {}

  async trackEvent(userId: string, eventName: CalendarAnalyticsEvent, entryId?: string): Promise<void> {
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
                  feature: 'content_calendar',
                  ...(entryId ? { entry_id: entryId } : {}),
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

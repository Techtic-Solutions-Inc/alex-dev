import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

type ContentLibraryAnalyticsEvent =
  | 'content_library_viewed'
  | 'content_library_created'
  | 'content_library_opened'
  | 'content_library_updated'
  | 'content_library_deleted'
  | 'content_library_searched';

@Injectable()
export class ContentLibraryAnalyticsService {
  private readonly logger = new Logger(ContentLibraryAnalyticsService.name);

  constructor(private readonly configService: ConfigService) {}

  async trackEvent(
    userId: string,
    eventName: ContentLibraryAnalyticsEvent,
    itemId?: string,
    query?: string,
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
                  feature: 'content_library',
                  ...(itemId ? { item_id: itemId } : {}),
                  ...(query ? { search_query: query } : {}),
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

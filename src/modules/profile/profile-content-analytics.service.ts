import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

type ProfileContentAnalyticsEvent =
  'profile_content_viewed' | 'profile_content_created' | 'profile_content_updated' | 'profile_content_deleted';

@Injectable()
export class ProfileContentAnalyticsService {
  private readonly logger = new Logger(ProfileContentAnalyticsService.name);

  constructor(private readonly configService: ConfigService) {}

  async trackEvent(userId: string, eventName: ProfileContentAnalyticsEvent, contentId?: string): Promise<void> {
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
                  feature: 'profile_content_generated',
                  ...(contentId ? { content_id: contentId } : {}),
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

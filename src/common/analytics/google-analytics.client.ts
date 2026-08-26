import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';

export type GoogleAnalyticsParams = Record<string, string | number | boolean | null>;

/**
 * Fire-and-forget Google Analytics Measurement Protocol client.
 * Credentials are optional; tracking is skipped when they are not configured.
 */
@Injectable()
export class GoogleAnalyticsClient {
  private readonly logger = new Logger(GoogleAnalyticsClient.name);

  constructor(private readonly configService: ConfigService) {}

  /**
   * Sends a single GA4 event via the Measurement Protocol collect endpoint.
   * Failures are logged and swallowed so product flows are never blocked by analytics.
   */
  async trackEvent(clientId: string, eventName: string, params: GoogleAnalyticsParams = {}): Promise<void> {
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
            client_id: clientId,
            user_id: clientId,
            events: [
              {
                name: eventName,
                params,
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

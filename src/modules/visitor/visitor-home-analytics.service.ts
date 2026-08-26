import { Injectable } from '@nestjs/common';
import { GoogleAnalyticsClient, GoogleAnalyticsParams } from '../../common/analytics/google-analytics.client';

export type VisitorHomeAnalyticsEvent =
  'visitor_home_searched' | 'visitor_home_subscribed' | 'visitor_home_terms_accepted';

/**
 * Tracks Visitor Home screen interactions through the shared Google Analytics client.
 */
@Injectable()
export class VisitorHomeAnalyticsService {
  constructor(private readonly googleAnalyticsClient: GoogleAnalyticsClient) {}

  /**
   * Records a Visitor Home analytics event without blocking the HTTP response.
   */
  async trackEvent(
    clientId: string,
    eventName: VisitorHomeAnalyticsEvent,
    metadata: GoogleAnalyticsParams = {},
  ): Promise<void> {
    await this.googleAnalyticsClient.trackEvent(clientId, eventName, {
      feature: 'visitor_home',
      ...metadata,
    });
  }
}

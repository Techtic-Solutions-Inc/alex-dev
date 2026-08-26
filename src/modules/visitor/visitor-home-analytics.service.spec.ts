import { Test, TestingModule } from '@nestjs/testing';
import { GoogleAnalyticsClient } from '../../common/analytics/google-analytics.client';
import { VisitorHomeAnalyticsService } from './visitor-home-analytics.service';

describe('VisitorHomeAnalyticsService', () => {
  it('trackEvent delegates to GoogleAnalyticsClient with the visitor_home feature', async () => {
    const googleAnalyticsClient = { trackEvent: jest.fn().mockResolvedValue(undefined) };
    const module: TestingModule = await Test.createTestingModule({
      providers: [VisitorHomeAnalyticsService, { provide: GoogleAnalyticsClient, useValue: googleAnalyticsClient }],
    }).compile();

    const service = module.get(VisitorHomeAnalyticsService);
    await service.trackEvent('visitor', 'visitor_home_searched', { search_query: 'templates' });

    expect(googleAnalyticsClient.trackEvent).toHaveBeenCalledWith('visitor', 'visitor_home_searched', {
      feature: 'visitor_home',
      search_query: 'templates',
    });
  });
});

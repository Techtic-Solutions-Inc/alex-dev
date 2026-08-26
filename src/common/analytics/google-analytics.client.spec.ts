import { ConfigService } from '@nestjs/config';
import { Test, TestingModule } from '@nestjs/testing';
import { GoogleAnalyticsClient } from './google-analytics.client';

describe('GoogleAnalyticsClient', () => {
  let client: GoogleAnalyticsClient;
  let configService: { get: jest.Mock };
  const originalFetch = global.fetch;

  beforeEach(async () => {
    configService = { get: jest.fn() };
    const module: TestingModule = await Test.createTestingModule({
      providers: [GoogleAnalyticsClient, { provide: ConfigService, useValue: configService }],
    }).compile();

    client = module.get(GoogleAnalyticsClient);
    global.fetch = jest.fn() as unknown as typeof fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
    jest.resetAllMocks();
  });

  it('no-ops when measurement id or api secret is missing', async () => {
    configService.get.mockReturnValue(undefined);

    await client.trackEvent('visitor', 'visitor_home_searched', { feature: 'visitor_home' });

    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('POSTs mp/collect with client_id, event name, and params when configured', async () => {
    configService.get.mockImplementation((key: string) => {
      if (key === 'GOOGLE_ANALYTICS_MEASUREMENT_ID') {
        return 'G-TEST';
      }
      if (key === 'GOOGLE_ANALYTICS_API_SECRET') {
        return 'secret';
      }
      return undefined;
    });
    (global.fetch as jest.Mock).mockResolvedValue({ ok: true });

    await client.trackEvent('jane.doe@example.com', 'visitor_home_subscribed', { feature: 'visitor_home' });

    expect(global.fetch).toHaveBeenCalledWith(
      'https://www.google-analytics.com/mp/collect?measurement_id=G-TEST&api_secret=secret',
      expect.objectContaining({
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          client_id: 'jane.doe@example.com',
          user_id: 'jane.doe@example.com',
          events: [{ name: 'visitor_home_subscribed', params: { feature: 'visitor_home' } }],
        }),
      }),
    );
  });

  it('logs a warning and does not throw when fetch rejects', async () => {
    configService.get.mockReturnValue('configured');
    (global.fetch as jest.Mock).mockRejectedValue(new Error('network down'));

    await expect(client.trackEvent('visitor', 'visitor_home_searched')).resolves.toBeUndefined();
  });

  it('logs a warning and does not throw when response.ok is false', async () => {
    configService.get.mockReturnValue('configured');
    (global.fetch as jest.Mock).mockResolvedValue({ ok: false, status: 500 });

    await expect(client.trackEvent('visitor', 'visitor_home_searched')).resolves.toBeUndefined();
  });
});

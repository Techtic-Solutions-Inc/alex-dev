import { HttpStatus } from '@nestjs/common';
import { getModelToken } from '@nestjs/mongoose';
import { Test, TestingModule } from '@nestjs/testing';
import { HttpException } from '../../common/exceptions/http.exception';
import { VisitorHomeContent } from './entities/visitor-home-content.schema';
import { VisitorHomeSubscription } from './entities/visitor-home-subscription.schema';
import { VisitorHomeAnalyticsService } from './visitor-home-analytics.service';
import { VisitorHomeService } from './visitor-home.service';

describe('VisitorHomeService', () => {
  let service: VisitorHomeService;
  let contentModel: {
    find: jest.Mock;
    countDocuments: jest.Mock;
  };
  let subscriptionModel: {
    findOne: jest.Mock;
    create: jest.Mock;
  };
  let analytics: { trackEvent: jest.Mock };

  const contentDoc = {
    _id: { toString: () => '66df0b7814b3e891e4ebcd21' },
    title: 'Luxury Listing Social Template',
    description: 'Ready-made templates for agents.',
    category: 'Social Media',
    tags: ['templates'],
    image_url: 'https://cdn.example.com/template.jpg',
    link: 'https://example.com/template',
    is_active: true,
    createdAt: new Date('2026-06-01T10:00:00.000Z'),
    updatedAt: new Date('2026-06-02T12:30:00.000Z'),
  };

  beforeEach(async () => {
    contentModel = {
      find: jest.fn(),
      countDocuments: jest.fn(),
    };
    subscriptionModel = {
      findOne: jest.fn(),
      create: jest.fn(),
    };
    analytics = { trackEvent: jest.fn().mockResolvedValue(undefined) };

    const module: TestingModule = await Test.createTestingModule({
      providers: [
        VisitorHomeService,
        { provide: getModelToken(VisitorHomeContent.name), useValue: contentModel },
        { provide: getModelToken(VisitorHomeSubscription.name), useValue: subscriptionModel },
        { provide: VisitorHomeAnalyticsService, useValue: analytics },
      ],
    }).compile();

    service = module.get(VisitorHomeService);
  });

  const mockFindChain = (items: unknown[]) => {
    contentModel.find.mockReturnValue({
      sort: () => ({
        skip: () => ({
          limit: () => ({
            exec: async () => items,
          }),
        }),
      }),
    });
    contentModel.countDocuments.mockReturnValue({
      exec: async () => items.length,
    });
  };

  const mockFindOne = (doc: unknown) => {
    subscriptionModel.findOne.mockReturnValue({
      collation: () => ({
        exec: async () => doc,
      }),
    });
  };

  it('searchContent returns matching active items and pagination for q', async () => {
    mockFindChain([contentDoc]);

    const result = await service.searchContent({ q: 'templates', page: 1, limit: 10 });

    expect(result.items).toHaveLength(1);
    expect(result.items[0]).toMatchObject({
      id: '66df0b7814b3e891e4ebcd21',
      name: contentDoc.title,
      title: contentDoc.title,
      description: contentDoc.description,
      link: contentDoc.link,
      error: null,
    });
    expect(result.pagination).toEqual({
      page: 1,
      limit: 10,
      total: 1,
      total_pages: 1,
      has_next_page: false,
      has_previous_page: false,
    });
    expect(analytics.trackEvent).toHaveBeenCalledWith('visitor', 'visitor_home_searched', {
      search_query: 'templates',
    });
  });

  it('searchContent returns empty items array when nothing matches', async () => {
    mockFindChain([]);

    const result = await service.searchContent({ q: 'missing', page: 1, limit: 10 });

    expect(result.items).toEqual([]);
    expect(result.pagination.total).toBe(0);
    expect(result.pagination.total_pages).toBe(0);
  });

  it('subscribe creates a lead when terms_accepted is true', async () => {
    mockFindOne(null);
    const created = {
      _id: { toString: () => '66df0b7814b3e891e4ebcd22' },
      full_name: 'Jane Doe',
      first_name: 'Jane',
      last_name: 'Doe',
      email: 'jane.doe@example.com',
      phone: '+1-555-0100',
      terms_accepted: true,
      subscribed: true,
      createdAt: new Date('2026-06-01T10:00:00.000Z'),
      updatedAt: new Date('2026-06-01T10:00:00.000Z'),
    };
    subscriptionModel.create.mockResolvedValue(created);

    const result = await service.subscribe({
      first_name: 'Jane',
      last_name: 'Doe',
      full_name: 'Jane Doe',
      email: 'jane.doe@example.com',
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(result.email).toBe('jane.doe@example.com');
    expect(result.subscribed).toBe(true);
    expect(result.phone_number).toBe('+1-555-0100');
    expect(result.error).toBeNull();
    expect(analytics.trackEvent).toHaveBeenCalledWith('jane.doe@example.com', 'visitor_home_subscribed');
  });

  it('subscribe throws 409 EMAIL_ALREADY_EXISTS when subscribed is already true', async () => {
    mockFindOne({ subscribed: true, email: 'jane.doe@example.com' });

    await expect(
      service.subscribe({
        full_name: 'Jane Doe',
        email: 'jane.doe@example.com',
        phone: '+1-555-0100',
        terms_accepted: true,
      }),
    ).rejects.toMatchObject<Partial<HttpException>>({
      status: HttpStatus.CONFLICT,
      code: 'EMAIL_ALREADY_EXISTS',
    });
  });

  it('subscribe upgrades a consent-only row instead of returning 409', async () => {
    const existing = {
      subscribed: false,
      terms_accepted_at: new Date('2026-05-01T00:00:00.000Z'),
      full_name: '',
      first_name: null,
      last_name: null,
      phone: null,
      save: jest.fn().mockImplementation(async function save(this: { subscribed: boolean }) {
        this.subscribed = true;
        return {
          ...this,
          _id: { toString: () => '66df0b7814b3e891e4ebcd23' },
          email: 'jane.doe@example.com',
          terms_accepted: true,
          subscribed: true,
          createdAt: new Date('2026-06-01T10:00:00.000Z'),
          updatedAt: new Date('2026-06-01T10:00:00.000Z'),
        };
      }),
    };
    mockFindOne(existing);

    const result = await service.subscribe({
      full_name: 'Jane Doe',
      email: 'jane.doe@example.com',
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(existing.save).toHaveBeenCalled();
    expect(result.subscribed).toBe(true);
  });

  it('subscribe throws VALIDATION_ERROR when name and phone cannot be resolved', async () => {
    mockFindOne(null);

    await expect(
      service.subscribe({
        email: 'jane.doe@example.com',
        terms_accepted: true,
      }),
    ).rejects.toMatchObject<Partial<HttpException>>({
      status: HttpStatus.BAD_REQUEST,
      code: 'VALIDATION_ERROR',
    });
  });

  it('subscribe maps Mongo 11000 to 409 EMAIL_ALREADY_EXISTS', async () => {
    mockFindOne(null);
    subscriptionModel.create.mockRejectedValue({ code: 11000 });

    await expect(
      service.subscribe({
        full_name: 'Jane Doe',
        email: 'jane.doe@example.com',
        phone: '+1-555-0100',
        terms_accepted: true,
      }),
    ).rejects.toMatchObject<Partial<HttpException>>({
      status: HttpStatus.CONFLICT,
      code: 'EMAIL_ALREADY_EXISTS',
    });
  });

  it('acceptTerms upserts terms_accepted and is idempotent if already accepted', async () => {
    mockFindOne(null);
    subscriptionModel.create.mockResolvedValue({
      _id: { toString: () => '66df0b7814b3e891e4ebcd24' },
      full_name: 'Jane Doe',
      first_name: 'Jane',
      last_name: 'Doe',
      email: 'jane.doe@example.com',
      phone: '+1-555-0100',
      terms_accepted: true,
      subscribed: false,
      createdAt: new Date('2026-06-01T10:00:00.000Z'),
      updatedAt: new Date('2026-06-01T10:00:00.000Z'),
    });

    const created = await service.acceptTerms({
      full_name: 'Jane Doe',
      email: 'jane.doe@example.com',
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(created.terms_accepted).toBe(true);
    expect(created.subscribed).toBe(false);

    const existing = {
      terms_accepted: true,
      subscribed: false,
      full_name: 'Jane Doe',
      first_name: 'Jane',
      last_name: 'Doe',
      phone: '+1-555-0100',
      save: jest.fn().mockResolvedValue({
        _id: { toString: () => '66df0b7814b3e891e4ebcd24' },
        full_name: 'Jane Doe',
        first_name: 'Jane',
        last_name: 'Doe',
        email: 'jane.doe@example.com',
        phone: '+1-555-0100',
        terms_accepted: true,
        subscribed: false,
        createdAt: new Date('2026-06-01T10:00:00.000Z'),
        updatedAt: new Date('2026-06-02T12:30:00.000Z'),
      }),
    };
    mockFindOne(existing);

    const repeated = await service.acceptTerms({
      email: 'jane.doe@example.com',
      terms_accepted: true,
    });

    expect(existing.save).toHaveBeenCalled();
    expect(repeated.terms_accepted).toBe(true);
    expect(analytics.trackEvent).toHaveBeenCalledWith('jane.doe@example.com', 'visitor_home_terms_accepted');
  });
});

import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { ContentLibraryModule } from '../src/modules/content-library/content-library.module';
import { ContentLibraryService } from '../src/modules/content-library/content-library.service';
import { getModelToken } from '@nestjs/mongoose';
import { ContentLibraryItem } from '../src/modules/content-library/entities/content-library-item.schema';
import { mockedContentLibraryItems } from './mockedContentLibraryItems';

describe('Content Library Search API (e2e)', () => {
  let app: INestApplication;
  let service: ContentLibraryService;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [ContentLibraryModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  beforeEach(async () => {
    jest.clearAllMocks();
  });

  it('should return relevant content items for a valid search query', async () => {
    jest.spyOn(service, 'searchPublicLibraryItems').mockResolvedValueOnce({
      items: mockedContentLibraryItems,
      pagination: { page: 1, limit: 20, total: 1, total_pages: 1, has_next_page: false, has_previous_page: false },
    });

    const response = await request(app.getHttpServer())
      .get('/api/content-library/search')
      .query({ query: 'luxury', full_name: 'Jane Doe', phone: '+1-555-0100' });

    expect(response.status).toBe(200);
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0].title).toBe('Luxury Listing Social Template');
  });

  it('should return 400 error for an empty search query', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/content-library/search')
      .query({ query: '' });

    expect(response.status).toBe(400);
    expect(response.body.message).toBe('Search query cannot be empty');
  });

  it('should return 404 error when no content items match the search query', async () => {
    jest.spyOn(service, 'searchPublicLibraryItems').mockRejectedValueOnce(new NotFoundException('No content library items matched the search query'));

    const response = await request(app.getHttpServer())
      .get('/api/content-library/search')
      .query({ query: 'nonexistent' });

    expect(response.status).toBe(404);
    expect(response.body.message).toBe('No content library items matched the search query');
  });

  it('should return 401 error for missing token', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/content-library/search')
      .query({ query: 'luxury' });

    expect(response.status).toBe(401);
    expect(response.body.message).toBe('Unauthorized');
  });
});

import { Test, TestingModule } from '@nestjs/testing';
import { ContentLibrarySearchController } from './content-library.search.controller';
import { ContentLibraryService } from './content-library.service';

describe('ContentLibrarySearchController', () => {
  let controller: ContentLibrarySearchController;
  const service: jest.Mocked<Pick<ContentLibraryService, 'searchPublicLibraryItems'>> = {
    searchPublicLibraryItems: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [ContentLibrarySearchController],
      providers: [{ provide: ContentLibraryService, useValue: service }],
    }).compile();

    controller = module.get(ContentLibrarySearchController);
    jest.clearAllMocks();
  });

  it('test_search_success', async () => {
    service.searchPublicLibraryItems.mockResolvedValue({
      items: [
        {
          id: '66df0b7814b3e891e4ebcd21',
          title: 'Luxury Listing Social Template',
          link: 'https://example.com/content-library/luxury-listing-template',
          description: 'Editable social post template designed for luxury property launches.',
          image: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
          image_url: 'https://cdn.example.com/content-library/luxury-listing-template.jpg',
          category: 'Social Media',
          tags: ['luxury'],
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
          error: null,
          is_active: true,
          created_at: '2026-06-01T10:00:00.000Z',
          updated_at: '2026-06-02T12:30:00.000Z',
        },
      ],
      pagination: {
        page: 1,
        limit: 20,
        total: 1,
        total_pages: 1,
        has_next_page: false,
        has_previous_page: false,
      },
    });

    const result = await controller.searchContentLibrary({
      query: 'luxury',
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
    });

    expect(service.searchPublicLibraryItems).toHaveBeenCalledWith({
      query: 'luxury',
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
    });
    expect(result.message).toBe('Content library search completed successfully');
    expect(result.data.items).toHaveLength(1);
    expect(result.data.items[0].title).toBe('Luxury Listing Social Template');
  });

  it('test_search_empty_query', async () => {
    const { HttpException } = await import('../../common/exceptions/http.exception');
    service.searchPublicLibraryItems.mockRejectedValue(
      new HttpException('Search query cannot be empty', 400, 'EMPTY_SEARCH_QUERY', {
        query: ['Search query cannot be empty'],
      }),
    );

    await expect(controller.searchContentLibrary({ query: '' })).rejects.toMatchObject({
      code: 'EMPTY_SEARCH_QUERY',
      status: 400,
    });
  });

  it('test_search_no_results', async () => {
    const { HttpException } = await import('../../common/exceptions/http.exception');
    service.searchPublicLibraryItems.mockRejectedValue(
      new HttpException(
        'No content library items matched the search query',
        404,
        'CONTENT_LIBRARY_SEARCH_NO_RESULTS',
      ),
    );

    await expect(controller.searchContentLibrary({ query: 'no-such-content' })).rejects.toMatchObject({
      code: 'CONTENT_LIBRARY_SEARCH_NO_RESULTS',
      status: 404,
    });
  });
});
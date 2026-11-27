import { Test, TestingModule } from '@nestjs/testing';
import { JwtAuthGuard } from '../../../common/guards/jwt.guard';
import { RolesGuard } from '../../../common/guards/roles.guard';
import { RealEstateProfessionalContentController } from './content.controller';
import { RealEstateProfessionalContentService } from './content.service';

describe('RealEstateProfessionalContentController', () => {
  let controller: RealEstateProfessionalContentController;
  const service: jest.Mocked<
    Pick<RealEstateProfessionalContentService, 'listItems' | 'createItem' | 'updateItem' | 'deleteItem'>
  > = {
    listItems: jest.fn(),
    createItem: jest.fn(),
    updateItem: jest.fn(),
    deleteItem: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [RealEstateProfessionalContentController],
      providers: [{ provide: RealEstateProfessionalContentService, useValue: service }],
    })
      .overrideGuard(JwtAuthGuard)
      .useValue({ canActivate: () => true })
      .overrideGuard(RolesGuard)
      .useValue({ canActivate: () => true })
      .compile();

    controller = module.get(RealEstateProfessionalContentController);
    jest.clearAllMocks();
  });

  it('test_get_content_list', async () => {
    service.listItems.mockResolvedValue({
      items: [],
      pagination: {
        page: 1,
        limit: 20,
        total: 0,
        total_pages: 0,
        has_next: false,
        has_previous: false,
      },
    });

    const result = await controller.listItems({ page: 1, limit: 20, sort: 'newest' });
    expect(service.listItems).toHaveBeenCalled();
    expect(result.message).toBe('Content items retrieved successfully');
  });

  it('test_create_content_item', async () => {
    service.createItem.mockResolvedValue({
      id: 'id',
      name: 'Title',
      description: 'Description',
      city: 'Austin',
      link: 'https://example.com',
      image_url: 'https://cdn.example.com/a.jpg',
      tags: [],
      phone: '+1-555-0100',
      error: null,
      created_at: '2026-01-01T00:00:00.000Z',
      updated_at: '2026-01-01T00:00:00.000Z',
    });

    const result = await controller.createItem(
      { user: { sub: 'user-id', tokenUse: 'access' } } as never,
      {
        title: 'Title',
        description: 'Description',
        image_url: 'https://cdn.example.com/a.jpg',
        tags: [],
        phone: '+1-555-0100',
        terms_accepted: true,
      },
    );

    expect(result.message).toBe('Content item created successfully');
    expect(service.createItem).toHaveBeenCalledWith('user-id', expect.any(Object));
  });

  it('test_update_content_item', async () => {
    service.updateItem.mockResolvedValue({
      id: 'id',
      name: 'Updated',
      description: 'Description',
      city: null,
      link: null,
      image_url: 'https://cdn.example.com/a.jpg',
      tags: [],
      phone: '+1-555-0100',
      error: null,
      created_at: '2026-01-01T00:00:00.000Z',
      updated_at: '2026-01-02T00:00:00.000Z',
    });

    const result = await controller.updateItem(
      { user: { sub: 'user-id', tokenUse: 'access' } } as never,
      'id',
      { title: 'Updated' },
    );

    expect(result.message).toBe('Content item updated successfully');
    expect(service.updateItem).toHaveBeenCalledWith('user-id', 'id', { title: 'Updated' });
  });

  it('test_delete_content_item', async () => {
    await controller.deleteItem({ user: { sub: 'user-id', tokenUse: 'access' } } as never, 'id');
    expect(service.deleteItem).toHaveBeenCalledWith('user-id', 'id');
  });
});
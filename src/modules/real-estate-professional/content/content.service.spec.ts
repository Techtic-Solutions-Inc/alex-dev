import { HttpException } from '../../../common/exceptions/http.exception';
import { RealEstateProfessionalContentService } from './content.service';
import { RealEstateContentItem } from './entities/content-item.schema';
import { Model, Types } from 'mongoose';

describe('RealEstateProfessionalContentService', () => {
  const buildService = (model: Partial<Model<RealEstateContentItem>>): RealEstateProfessionalContentService =>
    new RealEstateProfessionalContentService(model as Model<RealEstateContentItem>);

  it('rejects an empty search term with EMPTY_SEARCH_TERM', async () => {
    const service = buildService({});
    await expect(service.listItems({ sort: 'newest', page: 1, limit: 20, search: '   ' })).rejects.toMatchObject({
      status: 400,
      code: 'EMPTY_SEARCH_TERM',
    } satisfies Partial<HttpException>);
  });

  it('returns paginated list data with defaults', async () => {
    const userId = new Types.ObjectId();
    const record = {
      _id: new Types.ObjectId(),
      user_id: userId,
      title: 'Sample',
      description: 'Desc',
      image_url: 'https://cdn.example.com/a.jpg',
      link: null,
      city: 'Austin',
      tags: ['a'],
      phone: '+1-555-0100',
      is_active: true,
      createdAt: new Date('2026-01-01T00:00:00.000Z'),
      updatedAt: new Date('2026-01-02T00:00:00.000Z'),
    };

    const exec = jest.fn().mockResolvedValue([record]);
    const countExec = jest.fn().mockResolvedValue(1);
    const model = {
      find: jest.fn().mockReturnValue({ sort: () => ({ skip: () => ({ limit: () => ({ exec }) }) }) }),
      countDocuments: jest.fn().mockReturnValue({ exec: countExec }),
    };

    const service = buildService(model);
    const result = await service.listItems({ sort: 'newest', page: 1, limit: 20 });

    expect(result.items).toHaveLength(1);
    expect(result.items[0].name).toBe('Sample');
    expect(result.name).toBe('Sample');
    expect(result.id).toBe(record._id.toString());
    expect(result.city).toBe('Austin');
    expect(result.error).toBeNull();
    expect(result.pagination).toEqual(
      expect.objectContaining({
        page: 1,
        limit: 20,
        total: 1,
        has_next: false,
        has_previous: false,
      }),
    );
  });

  it('throws CONTENT_ALREADY_EXISTS when duplicate title is detected', async () => {
    const exists = jest.fn().mockReturnValue({ collation: () => Promise.resolve({ _id: 'dup' }) });
    const model = { exists };
    const service = buildService(model);

    await expect(
      service.createItem(new Types.ObjectId().toString(), {
        title: 'Dup',
        description: 'Desc',
        image_url: 'https://cdn.example.com/a.jpg',
        tags: ['x'],
        phone: '+1-555-0100',
        terms_accepted: true,
      }),
    ).rejects.toMatchObject({
      status: 409,
      code: 'CONTENT_ALREADY_EXISTS',
    } satisfies Partial<HttpException>);
  });
});

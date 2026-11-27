import { Test, TestingModule } from '@nestjs/testing';
import { JwtAuthGuard } from '../../../common/guards/jwt.guard';
import { RolesGuard } from '../../../common/guards/roles.guard';
import { BlogDetailAccessGuard } from './blog-detail.guard';
import { RealEstateProfessionalBlogController } from './blog.controller';
import { RealEstateProfessionalBlogService } from './blog.service';

describe('RealEstateProfessionalBlogController', () => {
  let controller: RealEstateProfessionalBlogController;
  const service: jest.Mocked<
    Pick<RealEstateProfessionalBlogService, 'listPosts' | 'getPostById' | 'createPost' | 'updatePost' | 'deletePost'>
  > = {
    listPosts: jest.fn(),
    getPostById: jest.fn(),
    createPost: jest.fn(),
    updatePost: jest.fn(),
    deletePost: jest.fn(),
  };

  const detail = {
    id: 'blog-id',
    title: 'Hates to see me coming',
    author_email: 'hello@agentwisemarketing.com',
    content: 'Lorem Ipsum',
    description: 'Preview text',
    link: 'https://example.com/blog/post',
    phone: '+1-555-0100',
    terms_accepted: true,
    metadata: { created_at: '2026-01-01T00:00:00.000Z', updated_at: '2026-01-01T00:00:00.000Z' },
    error: null,
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [RealEstateProfessionalBlogController],
      providers: [{ provide: RealEstateProfessionalBlogService, useValue: service }],
    })
      .overrideGuard(JwtAuthGuard)
      .useValue({ canActivate: () => true })
      .overrideGuard(RolesGuard)
      .useValue({ canActivate: () => true })
      .overrideGuard(BlogDetailAccessGuard)
      .useValue({ canActivate: () => true })
      .compile();

    controller = module.get(RealEstateProfessionalBlogController);
    jest.clearAllMocks();
  });

  it('test_get_blog_success — lists posts', async () => {
    service.listPosts.mockResolvedValue({
      items: [
        {
          ...detail,
          image_url: 'https://cdn.example.com/blog.jpg',
        },
      ],
      pagination: {
        page: 1,
        limit: 20,
        total: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
      id: detail.id,
      title: detail.title,
      description: detail.description,
      link: detail.link,
      error: null,
    });

    const result = await controller.listPosts({ page: 1, limit: 20, sort: 'newest' });
    expect(service.listPosts).toHaveBeenCalled();
    expect(result.message).toBe('Blog posts retrieved successfully');
  });

  it('test_create_blog_success — creates a post', async () => {
    service.createPost.mockResolvedValue(detail);

    const result = await controller.createPost({ user: { sub: 'user-id', tokenUse: 'access' } } as never, {
      title: detail.title,
      author_email: detail.author_email,
      content: detail.content,
      description: detail.description,
      image_url: 'https://cdn.example.com/blog.jpg',
      phone: detail.phone,
      terms_accepted: true,
    });

    expect(service.createPost).toHaveBeenCalledWith('user-id', expect.any(Object));
    expect(result.data.title).toBe(detail.title);
  });

  it('test_update_blog_success — updates a post', async () => {
    service.updatePost.mockResolvedValue({ ...detail, title: 'Updated title' });

    const result = await controller.updatePost({ user: { sub: 'user-id', tokenUse: 'access' } } as never, 'blog-id', {
      title: 'Updated title',
    });

    expect(service.updatePost).toHaveBeenCalledWith('user-id', 'blog-id', { title: 'Updated title' });
    expect(result.data.title).toBe('Updated title');
  });

  it('test_delete_blog_success — deletes a post', async () => {
    service.deletePost.mockResolvedValue(undefined);

    await controller.deletePost({ user: { sub: 'user-id', tokenUse: 'access' } } as never, 'blog-id');

    expect(service.deletePost).toHaveBeenCalledWith('user-id', 'blog-id');
  });

  it('returns blog detail by id', async () => {
    service.getPostById.mockResolvedValue(detail);

    const result = await controller.getPostById('blog-id');
    expect(service.getPostById).toHaveBeenCalledWith('blog-id');
    expect(result.data).toMatchObject({
      title: detail.title,
      author_email: detail.author_email,
      content: detail.content,
      metadata: detail.metadata,
    });
  });
});

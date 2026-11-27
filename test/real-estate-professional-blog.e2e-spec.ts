import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { JwtService } from '@nestjs/jwt';

describe('Blog API (e2e)', () => {
  let app: INestApplication;
  let jwtService: JwtService;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    jwtService = app.get<JwtService>(JwtService);
  });

  afterAll(async () => {
    await app.close();
  });

  it('GET /api/blog should return a list of blog posts', async () => {
    const response = await request(app.getHttpServer()).get('/api/blog').expect(200);
    expect(Array.isArray(response.body)).toBe(true);
  });

  it('POST /api/blog should create a new blog post', async () => {
    const token = jwtService.sign({ sub: 'admin-user' });
    const response = await request(app.getHttpServer())
      .post('/api/blog')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'New Blog', author_email: 'author@example.com', content: 'Content', terms_accepted: true })
      .expect(201);
    expect(response.body.title).toEqual('New Blog');
  });

  it('POST /api/blog with empty title should return 400', async () => {
    const token = jwtService.sign({ sub: 'admin-user' });
    await request(app.getHttpServer())
      .post('/api/blog')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: '', author_email: 'author@example.com', content: 'Content', terms_accepted: true })
      .expect(400);
  });

  it('POST /api/blog with duplicate title should return 409', async () => {
    const token = jwtService.sign({ sub: 'admin-user' });
    await request(app.getHttpServer())
      .post('/api/blog')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'New Blog', author_email: 'author@example.com', content: 'Content', terms_accepted: true })
      .expect(409);
  });

  it('GET /api/blog/:id should return blog details', async () => {
    const token = jwtService.sign({ sub: 'admin-user' });
    const createResponse = await request(app.getHttpServer())
      .post('/api/blog')
      .set('Authorization', `Bearer ${token}`)
      .send({ title: 'Another Blog', author_email: 'author@example.com', content: 'Content', terms_accepted: true });
    const blogId = createResponse.body.id;

    const response = await request(app.getHttpServer()).get(`/api/blog/${blogId}`).expect(200);
    expect(response.body.title).toEqual('Another Blog');
  });

  it('GET /api/blog/:id should return 404 for non-existent blog', async () => {
    await request(app.getHttpServer()).get('/api/blog/non-existent-id').expect(404);
  });

  it('GET /api/blog/:id should return 403 for unauthorized users', async () => {
    await request(app.getHttpServer()).get('/api/blog/some-id').expect(403);
  });
});

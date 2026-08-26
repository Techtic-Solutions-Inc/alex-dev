import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, clearVisitorHome, createTestApp, uniqueEmail } from './create-test-app';
import {
  VISITOR_HOME_CONTENT_SEED,
  VisitorHomePersonas,
  installThirdPartyMocks,
  seedVisitorHomeContent,
  seedVisitorHomePersonas,
} from './visitor-home.fixtures';

describe('Visitor Home API integration (e2e)', () => {
  let app: INestApplication;
  let personas: VisitorHomePersonas;
  let fetchMock: jest.SpyInstance;
  const originalFetch = global.fetch;

  beforeAll(async () => {
    fetchMock = installThirdPartyMocks();
    app = await createTestApp();
    await clearUsers(app);
    await clearVisitorHome(app);
    personas = await seedVisitorHomePersonas(app);
  });

  afterAll(async () => {
    await clearVisitorHome(app);
    await clearUsers(app);
    await app.close();
    fetchMock.mockRestore();
    global.fetch = originalFetch;
  });

  beforeEach(async () => {
    await clearVisitorHome(app);
    fetchMock.mockClear();
  });

  function subscribePayload(overrides: Record<string, unknown> = {}) {
    return {
      full_name: 'Jane Doe',
      email: uniqueEmail('visitor.subscribe'),
      phone: '+1-555-0100',
      terms_accepted: true,
      ...overrides,
    };
  }

  it('seeds admin, agent, viewer analogue, and inactive users; new user is not in the database', async () => {
    const connection = app.get<Connection>(getConnectionToken());
    const emails = [personas.admin.email, personas.user.email, personas.viewer.email, personas.inactive.email];
    const inserted = await connection
      .collection('users')
      .find({ email: { $in: emails } })
      .toArray();

    expect(inserted).toHaveLength(4);
    expect(inserted.find((row) => row.email === personas.admin.email)?.role).toBe('admin');
    expect(inserted.find((row) => row.email === personas.user.email)?.role).toBe('agent');
    expect(inserted.find((row) => row.email === personas.viewer.email)?.role).toBe('marketing_manager');
    expect(inserted.find((row) => row.email === personas.inactive.email)?.is_active).toBe(false);

    const newUser = await connection.collection('users').findOne({ email: personas.new.email });
    expect(newUser).toBeNull();
    expect(personas.admin.accessToken).toEqual(expect.any(String));
    expect(personas.user.accessToken).toEqual(expect.any(String));
    expect(personas.viewer.accessToken).toEqual(expect.any(String));
  });

  it('GET /api/visitor/home/search returns 200 with relevant content for q (JAW-9136 AC)', async () => {
    const id = await seedVisitorHomeContent(app);

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q: 'templates' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Visitor home search completed successfully');
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0]).toMatchObject({
      id,
      name: VISITOR_HOME_CONTENT_SEED.title,
      title: VISITOR_HOME_CONTENT_SEED.title,
      description: VISITOR_HOME_CONTENT_SEED.description,
      link: VISITOR_HOME_CONTENT_SEED.link,
      image: VISITOR_HOME_CONTENT_SEED.image_url,
      image_url: VISITOR_HOME_CONTENT_SEED.image_url,
      category: VISITOR_HOME_CONTENT_SEED.category,
      tags: VISITOR_HOME_CONTENT_SEED.tags,
      full_name: null,
      first_name: null,
      last_name: null,
      email: null,
      phone: null,
      phone_number: null,
      error: null,
      is_active: true,
    });
    expect(response.body.data.pagination).toEqual({
      page: 1,
      limit: 10,
      total: 1,
      total_pages: 1,
      has_next_page: false,
      has_previous_page: false,
    });
  });

  it('GET /api/visitor/home/search filters by category', async () => {
    await seedVisitorHomeContent(app);
    await seedVisitorHomeContent(app, {
      title: 'Email Drip Campaign',
      description: 'Nurture leads with email sequences.',
      category: 'Email',
      tags: ['email'],
    });

    const response = await request(app.getHttpServer())
      .get('/api/visitor/home/search')
      .query({ category: 'Social Media' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0].category).toBe('Social Media');
    expect(response.body.data.items[0].title).toBe(VISITOR_HOME_CONTENT_SEED.title);
  });

  it('GET /api/visitor/home/search returns 200 with items [] when nothing matches', async () => {
    await seedVisitorHomeContent(app);

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q: 'nomatch-xyz' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toEqual([]);
    expect(response.body.data.pagination.total).toBe(0);
    expect(response.body.data.pagination.total_pages).toBe(0);
  });

  it('GET /api/visitor/home/search escapes regex metacharacters in q', async () => {
    await seedVisitorHomeContent(app);

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q: '.*' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toEqual([]);
  });

  it('GET /api/visitor/home/search matches unicode titles', async () => {
    const id = await seedVisitorHomeContent(app, {
      title: 'モデルホーム テンプレート',
      description: '日本語のマーケティングコンテンツ',
      tags: ['日本語'],
    });

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q: 'テンプレート' });

    expect(response.status).toBe(200);
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0].id).toBe(id);
    expect(response.body.data.items[0].title).toBe('モデルホーム テンプレート');
  });

  it('GET /api/visitor/home/search accepts a 120-character q', async () => {
    await seedVisitorHomeContent(app);
    const q = 't'.repeat(120);

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toEqual([]);
  });

  it('GET /api/visitor/home/search omits inactive content', async () => {
    await seedVisitorHomeContent(app, { is_active: false, title: 'Hidden Draft Template' });

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q: 'Hidden' });

    expect(response.status).toBe(200);
    expect(response.body.data.items).toEqual([]);
    expect(response.body.data.pagination.total).toBe(0);
  });

  it('GET /api/visitor/home/search paginates with limit and page', async () => {
    await seedVisitorHomeContent(app, {
      title: 'Alpha Template',
      tags: ['page-test'],
      updatedAt: new Date('2026-06-03T00:00:00.000Z'),
    });
    await seedVisitorHomeContent(app, {
      title: 'Beta Template',
      tags: ['page-test'],
      updatedAt: new Date('2026-06-04T00:00:00.000Z'),
    });

    const page1 = await request(app.getHttpServer())
      .get('/api/visitor/home/search')
      .query({ q: 'page-test', page: 1, limit: 1 });
    const page2 = await request(app.getHttpServer())
      .get('/api/visitor/home/search')
      .query({ q: 'page-test', page: 2, limit: 1 });

    expect(page1.status).toBe(200);
    expect(page1.body.data.items).toHaveLength(1);
    expect(page1.body.data.pagination).toMatchObject({
      page: 1,
      limit: 1,
      total: 2,
      total_pages: 2,
      has_next_page: true,
      has_previous_page: false,
    });
    expect(page2.status).toBe(200);
    expect(page2.body.data.items).toHaveLength(1);
    expect(page2.body.data.pagination).toMatchObject({
      page: 2,
      limit: 1,
      has_next_page: false,
      has_previous_page: true,
    });
    expect(page1.body.data.items[0].id).not.toBe(page2.body.data.items[0].id);
  });

  it('GET /api/visitor/home/search returns 400 for an empty q string', async () => {
    const response = await request(app.getHttpServer()).get('/api/visitor/home/search?q=');

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('GET /api/visitor/home/search returns 400 when page is below 1', async () => {
    const response = await request(app.getHttpServer()).get('/api/visitor/home/search?page=0');

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.page).toEqual(expect.arrayContaining([expect.any(String)]));
  });

  it('GET /api/visitor/home/search returns 400 when q exceeds 120 characters', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/visitor/home/search')
      .query({ q: 'q'.repeat(121) });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.q).toEqual(expect.arrayContaining([expect.any(String)]));
  });

  it('GET /api/visitor/home/search returns 400 for unknown query parameters', async () => {
    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ unexpected: 'nope' });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('GET /api/visitor/home/search is public and succeeds without Authorization', async () => {
    const response = await request(app.getHttpServer()).get('/api/visitor/home/search');

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toEqual([]);
  });

  it('GET /api/visitor/home/search ignores an invalid bearer token and still returns 200', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/visitor/home/search')
      .set('Authorization', 'Bearer not-a-valid-jwt');

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
  });

  it('GET /api/visitor/home/search still returns 200 when an admin bearer token is sent', async () => {
    await seedVisitorHomeContent(app);

    const response = await request(app.getHttpServer())
      .get('/api/visitor/home/search')
      .set('Authorization', `Bearer ${personas.admin.accessToken}`)
      .query({ q: 'templates' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toHaveLength(1);
  });

  it('POST /api/visitor/home/subscribe with Figma fields returns 201 and frontend contract fields', async () => {
    const email = uniqueEmail('visitor.subscribe.figma');

    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      full_name: 'Jane Doe',
      email,
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body).toEqual({
      success: true,
      message: 'Subscribed successfully',
      data: {
        id: expect.any(String),
        name: 'Jane Doe',
        full_name: 'Jane Doe',
        first_name: 'Jane',
        last_name: 'Doe',
        email,
        phone: '+1-555-0100',
        phone_number: '+1-555-0100',
        link: null,
        description: null,
        terms_accepted: true,
        subscribed: true,
        error: null,
        created_at: expect.any(String),
        updated_at: expect.any(String),
      },
    });
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('https://www.google-analytics.com/mp/collect'),
      expect.objectContaining({ method: 'POST' }),
    );
  });

  it('POST /api/visitor/home/subscribe accepts first_name, last_name, and phone_number aliases', async () => {
    const email = uniqueEmail('visitor.subscribe.aliases');

    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      phone_number: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.data).toMatchObject({
      name: 'Jane Doe',
      full_name: 'Jane Doe',
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      phone: '+1-555-0100',
      phone_number: '+1-555-0100',
      subscribed: true,
      error: null,
    });
  });

  it('POST /api/visitor/home/subscribe without terms_accepted returns 400 VALIDATION_ERROR (JAW-9136 AC)', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        full_name: 'Jane Doe',
        email: uniqueEmail('visitor.terms.missing'),
        phone: '+1-555-0100',
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Validation failed');
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: expect.objectContaining({
        terms_accepted: expect.arrayContaining([expect.any(String)]),
      }),
    });
  });

  it('POST /api/visitor/home/subscribe with terms_accepted false returns 400 VALIDATION_ERROR (JAW-9136 AC)', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        full_name: 'Jane Doe',
        email: uniqueEmail('visitor.terms.false'),
        phone: '+1-555-0100',
        terms_accepted: false,
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        terms_accepted: ['terms_accepted must be true'],
      },
    });
  });

  it('POST /api/visitor/home/subscribe duplicate email returns 409 EMAIL_ALREADY_EXISTS (JAW-9136 AC)', async () => {
    const email = uniqueEmail('visitor.duplicate');
    const payload = {
      full_name: 'Jane Doe',
      email,
      phone: '+1-555-0100',
      terms_accepted: true,
    };

    await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send(payload).expect(201);

    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({ ...payload, full_name: 'Janet Doe' });

    expect(response.status).toBe(409);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('This email address is already subscribed');
    expect(response.body.error).toEqual({
      code: 'EMAIL_ALREADY_EXISTS',
      details: {
        email: ['This email address is already subscribed'],
      },
    });
  });

  it('POST /api/visitor/home/subscribe accepts a unicode display name', async () => {
    const email = uniqueEmail('visitor.unicode');

    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      full_name: 'José María 李',
      email,
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.data.full_name).toBe('José María 李');
    expect(response.body.data.first_name).toBe('José');
    expect(response.body.data.last_name).toBe('María 李');
    expect(response.body.data.email).toBe(email);
  });

  it('POST /api/visitor/home/subscribe accepts a 160-character full_name', async () => {
    const email = uniqueEmail('visitor.max.name');
    const fullName = `${'A'.repeat(80)} ${'B'.repeat(79)}`;

    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      full_name: fullName,
      email,
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.data.full_name).toBe(fullName);
  });

  it('POST /api/visitor/home/subscribe trims and lowercases email', async () => {
    const local = uniqueEmail('visitor.normalize').split('@')[0];
    const mixed = `  ${local.toUpperCase()}@Example.COM  `;

    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      full_name: 'Jane Doe',
      email: mixed,
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.data.email).toBe(`${local}@example.com`);
  });

  it('POST /api/visitor/home/subscribe returns 400 for an invalid email (JAW-9136 AC)', async () => {
    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      full_name: 'Jane Doe',
      email: 'not-an-email',
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.email).toEqual(expect.arrayContaining([expect.any(String)]));
  });

  it('POST /api/visitor/home/subscribe returns 400 for an invalid phone (JAW-9136 AC)', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        full_name: 'Jane Doe',
        email: uniqueEmail('visitor.bad.phone'),
        phone: 'abc',
        terms_accepted: true,
      });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.phone).toEqual(expect.arrayContaining([expect.any(String)]));
  });

  it('POST /api/visitor/home/subscribe returns 400 when unknown JSON keys are submitted', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        ...subscribePayload(),
        unexpected_field: 'nope',
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('POST /api/visitor/home/subscribe returns 400 when name and phone cannot be resolved', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        email: uniqueEmail('visitor.missing.identity'),
        terms_accepted: true,
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
  });

  it('POST /api/visitor/home/subscribe is public and succeeds without Authorization', async () => {
    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send(subscribePayload());

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data.subscribed).toBe(true);
  });

  it('POST /api/visitor/home/subscribe treats case-insensitive duplicate emails as 409', async () => {
    const local = uniqueEmail('visitor.case').split('@')[0];
    const email = `${local}@example.com`;

    await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send(subscribePayload({ email }))
      .expect(201);

    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send(subscribePayload({ email: `${local.toUpperCase()}@EXAMPLE.COM` }));

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('EMAIL_ALREADY_EXISTS');
  });

  it('POST /api/visitor/home/subscribe does not insert a users collection document', async () => {
    const email = uniqueEmail('visitor.not.user');
    await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send(subscribePayload({ email }))
      .expect(201);

    const connection = app.get<Connection>(getConnectionToken());
    const user = await connection.collection('users').findOne({ email });
    const lead = await connection.collection('visitor_home_subscriptions').findOne({ email });

    expect(user).toBeNull();
    expect(lead).toBeTruthy();
    expect(lead?.subscribed).toBe(true);
  });

  it('POST /api/visitor/home/subscribe allows a visitor lead email that already exists on a user', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        full_name: `${personas.user.first_name} ${personas.user.last_name}`,
        email: personas.user.email,
        phone: '+1-555-0100',
        terms_accepted: true,
      });

    expect(response.status).toBe(201);
    expect(response.body.data.email).toBe(personas.user.email);
    expect(response.body.data.subscribed).toBe(true);

    const connection = app.get<Connection>(getConnectionToken());
    const user = await connection.collection('users').findOne({ email: personas.user.email });
    expect(user).toBeTruthy();
  });

  it('POST /api/visitor/home/terms-acceptance with terms_accepted true returns 201 (JAW-9136 AC)', async () => {
    const email = uniqueEmail('visitor.terms.ok');

    const response = await request(app.getHttpServer()).post('/api/visitor/home/terms-acceptance').send({
      full_name: 'Jane Doe',
      email,
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Terms and privacy policy accepted successfully');
    expect(response.body.data).toMatchObject({
      name: 'Jane Doe',
      full_name: 'Jane Doe',
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      phone: '+1-555-0100',
      phone_number: '+1-555-0100',
      link: null,
      description: null,
      terms_accepted: true,
      subscribed: false,
      error: null,
    });
    expect(response.body.data.id).toEqual(expect.any(String));
    expect(response.body.data.created_at).toEqual(expect.any(String));
  });

  it('POST /api/visitor/home/terms-acceptance is idempotent and still returns 201', async () => {
    const email = uniqueEmail('visitor.terms.idempotent');
    const payload = { email, terms_accepted: true };

    const first = await request(app.getHttpServer()).post('/api/visitor/home/terms-acceptance').send(payload);
    const second = await request(app.getHttpServer()).post('/api/visitor/home/terms-acceptance').send(payload);

    expect(first.status).toBe(201);
    expect(second.status).toBe(201);
    expect(second.body.data.id).toBe(first.body.data.id);
    expect(second.body.data.terms_accepted).toBe(true);
    expect(second.body.data.subscribed).toBe(false);
  });

  it('POST /api/visitor/home/terms-acceptance accepts email-only payloads', async () => {
    const email = uniqueEmail('visitor.terms.emailonly');

    const response = await request(app.getHttpServer()).post('/api/visitor/home/terms-acceptance').send({
      email,
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.data.email).toBe(email);
    expect(response.body.data.terms_accepted).toBe(true);
    expect(response.body.data.subscribed).toBe(false);
    expect(response.body.data.phone).toBeNull();
  });

  it('POST /api/visitor/home/terms-acceptance accepts first_name, last_name, and phone_number aliases', async () => {
    const email = uniqueEmail('visitor.terms.aliases');

    const response = await request(app.getHttpServer()).post('/api/visitor/home/terms-acceptance').send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      phone_number: '+1-555-0199',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.data).toMatchObject({
      full_name: 'Jane Doe',
      first_name: 'Jane',
      last_name: 'Doe',
      phone: '+1-555-0199',
      phone_number: '+1-555-0199',
      subscribed: false,
    });
  });

  it('POST /api/visitor/home/terms-acceptance with terms_accepted false returns 400', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/terms-acceptance')
      .send({
        email: uniqueEmail('visitor.terms.reject'),
        terms_accepted: false,
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        terms_accepted: ['terms_accepted must be true'],
      },
    });
  });

  it('POST /api/visitor/home/terms-acceptance returns 400 for an invalid email', async () => {
    const response = await request(app.getHttpServer()).post('/api/visitor/home/terms-acceptance').send({
      email: 'not-an-email',
      terms_accepted: true,
    });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.email).toEqual(expect.arrayContaining([expect.any(String)]));
  });

  it('POST /api/visitor/home/terms-acceptance is public and succeeds without Authorization', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/terms-acceptance')
      .send({
        email: uniqueEmail('visitor.terms.public'),
        terms_accepted: true,
      });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
  });

  it('upgrades a terms-only lead to subscribed instead of returning 409', async () => {
    const email = uniqueEmail('visitor.upgrade');

    await request(app.getHttpServer())
      .post('/api/visitor/home/terms-acceptance')
      .send({
        first_name: 'Jane',
        last_name: 'Doe',
        email,
        phone: '+1-555-0100',
        terms_accepted: true,
      })
      .expect(201);

    const response = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(response.status).toBe(201);
    expect(response.body.data.subscribed).toBe(true);
    expect(response.body.data.terms_accepted).toBe(true);
    expect(response.body.data.email).toBe(email);
  });

  it('GET /api/profile without a token returns 401 while visitor home stays public', async () => {
    const profile = await request(app.getHttpServer()).get('/api/profile');
    const search = await request(app.getHttpServer()).get('/api/visitor/home/search');

    expect(profile.status).toBe(401);
    expect(profile.body.success).toBe(false);
    expect(profile.body.error.code).toBe('AUTHENTICATION_REQUIRED');
    expect(search.status).toBe(200);
    expect(search.body.success).toBe(true);
  });

  it('inactive user cannot log in but can still use public visitor home endpoints', async () => {
    const login = await request(app.getHttpServer()).post('/api/auth/login').send({
      email: personas.inactive.email,
      password: personas.inactive.password,
    });
    const search = await request(app.getHttpServer())
      .get('/api/visitor/home/search')
      .set('Authorization', `Bearer ${personas.inactive.accessToken}`);

    expect(login.status).toBe(403);
    expect(login.body.error.code).toBe('USER_INACTIVE');
    expect(search.status).toBe(200);
    expect(search.body.success).toBe(true);
  });

  it('returns 400 when full_name exceeds 160 characters', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        full_name: 'A'.repeat(161),
        email: uniqueEmail('visitor.name.too.long'),
        phone: '+1-555-0100',
        terms_accepted: true,
      });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.full_name).toEqual(expect.arrayContaining([expect.any(String)]));
  });
});

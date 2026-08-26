import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearVisitorHome, createTestApp, uniqueEmail } from './create-test-app';

describe('Visitor Home (e2e)', () => {
  let app: INestApplication;

  const contentSeed = {
    title: 'Luxury Listing Social Template',
    description: 'Help real estate professionals create content faster with ready-made templates.',
    category: 'Social Media',
    tags: ['templates', 'instagram', 'listing'],
    image_url: 'https://cdn.example.com/visitor/home/luxury-listing-template.jpg',
    link: 'https://example.com/visitor/home/luxury-listing-template',
    is_active: true,
  };

  beforeAll(async () => {
    app = await createTestApp();
  });

  afterAll(async () => {
    await clearVisitorHome(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearVisitorHome(app);
  });

  async function seedContent(): Promise<string> {
    const connection = app.get<Connection>(getConnectionToken());
    const inserted = await connection.collection('visitor_home_contents').insertOne({
      ...contentSeed,
      createdAt: new Date('2026-06-01T10:00:00.000Z'),
      updatedAt: new Date('2026-06-02T12:30:00.000Z'),
    });
    return inserted.insertedId.toString();
  }

  it('GET /api/visitor/home/search returns 200 and relevant items for q', async () => {
    const id = await seedContent();

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q: 'templates' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Visitor home search completed successfully');
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0]).toMatchObject({
      id,
      name: contentSeed.title,
      title: contentSeed.title,
      description: contentSeed.description,
      link: contentSeed.link,
      image: contentSeed.image_url,
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

  it('GET /api/visitor/home/search returns 200 with items [] when q matches nothing', async () => {
    await seedContent();

    const response = await request(app.getHttpServer()).get('/api/visitor/home/search').query({ q: 'nomatch-xyz' });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toEqual([]);
    expect(response.body.data.pagination.total).toBe(0);
  });

  it('GET /api/visitor/home/search is public and does not require Authorization', async () => {
    const response = await request(app.getHttpServer()).get('/api/visitor/home/search');

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toEqual([]);
  });

  it('POST /api/visitor/home/subscribe without terms_accepted returns 400 VALIDATION_ERROR', async () => {
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

  it('POST /api/visitor/home/subscribe with terms_accepted false returns 400 VALIDATION_ERROR', async () => {
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

  it('POST /api/visitor/home/subscribe duplicate email returns 409 EMAIL_ALREADY_EXISTS', async () => {
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
      .send({
        ...payload,
        full_name: 'Janet Doe',
      });

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

  it('POST /api/visitor/home/subscribe with Figma fields returns 201', async () => {
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
    });
  });

  it('POST /api/visitor/home/terms-acceptance with terms_accepted true returns 201', async () => {
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
      email,
      phone: '+1-555-0100',
      phone_number: '+1-555-0100',
      terms_accepted: true,
      subscribed: false,
      error: null,
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

  it('returns 400 VALIDATION_ERROR for invalid email and invalid phone', async () => {
    const emailResponse = await request(app.getHttpServer()).post('/api/visitor/home/subscribe').send({
      full_name: 'Jane Doe',
      email: 'not-an-email',
      phone: '+1-555-0100',
      terms_accepted: true,
    });

    expect(emailResponse.status).toBe(400);
    expect(emailResponse.body.error.code).toBe('VALIDATION_ERROR');
    expect(emailResponse.body.error.details.email).toEqual(expect.arrayContaining([expect.any(String)]));

    const phoneResponse = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        full_name: 'Jane Doe',
        email: uniqueEmail('visitor.bad.phone'),
        phone: 'abc',
        terms_accepted: true,
      });

    expect(phoneResponse.status).toBe(400);
    expect(phoneResponse.body.error.code).toBe('VALIDATION_ERROR');
    expect(phoneResponse.body.error.details.phone).toEqual(expect.arrayContaining([expect.any(String)]));
  });

  it('returns 400 when unknown JSON keys are submitted', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/visitor/home/subscribe')
      .send({
        full_name: 'Jane Doe',
        email: uniqueEmail('visitor.unknown'),
        phone: '+1-555-0100',
        terms_accepted: true,
        unexpected_field: 'nope',
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
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
  });
});

import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Content Calendar (e2e)', () => {
  let app: INestApplication;
  let authToken: string;

  const validEntry = {
    title: 'Market update - Austin Q2',
    date: '2026-06-15T00:00:00Z',
    content:
      'Your personal content calendar designed to grow your business - made specifically for you. Drag, drop, edit, and curate your perfect content strategy or feel free to use this one already made for you.',
    full_name: 'Jane Doe',
    phone: '+1-555-0100',
  };

  beforeAll(async () => {
    app = await createTestApp();
    authToken = await createAuthenticatedToken(app);
  });

  afterAll(async () => {
    await clearCalendarEntries(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearCalendarEntries(app);
  });

  it('creates a content entry with valid data', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validEntry);

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content entry created successfully');
    expect(response.body.data).toMatchObject({
      id: expect.any(String),
      title: validEntry.title,
      date: '2026-06-15T00:00:00.000Z',
      content: validEntry.content,
      description: validEntry.content,
      full_name: validEntry.full_name,
      phone: validEntry.phone,
      link: null,
      error: null,
      is_active: true,
      created_at: expect.any(String),
      updated_at: expect.any(String),
    });
  });

  it('returns 400 when required fields are missing on create', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        content: validEntry.content,
        full_name: validEntry.full_name,
        phone: validEntry.phone,
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Validation failed');
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual(
      expect.objectContaining({
        title: expect.any(Array),
        date: expect.any(Array),
      }),
    );
  });

  it('returns 409 when creating a duplicate title on the same date', async () => {
    await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validEntry)
      .expect(201);

    const response = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validEntry);

    expect(response.status).toBe(409);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('CONTENT_ENTRY_ALREADY_EXISTS');
  });

  it('updates an existing content entry with valid data', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validEntry)
      .expect(201);

    const response = await request(app.getHttpServer())
      .put(`/api/content-calendar/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Market update - Austin Q2 revised',
        content: 'Updated content strategy tailored for Austin listings.',
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Content entry updated successfully');
    expect(response.body.data).toMatchObject({
      id: created.body.data.id,
      title: 'Market update - Austin Q2 revised',
      content: 'Updated content strategy tailored for Austin listings.',
      description: 'Updated content strategy tailored for Austin listings.',
    });
  });

  it('returns 404 when updating a non-existent content entry', async () => {
    const response = await request(app.getHttpServer())
      .put('/api/content-calendar/66df0b7814b3e891e4ebcd21')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ title: 'Missing entry update' });

    expect(response.status).toBe(404);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('CONTENT_ENTRY_NOT_FOUND');
  });

  it('deletes a content entry with 204 and no body', async () => {
    const created = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validEntry)
      .expect(201);

    const response = await request(app.getHttpServer())
      .delete(`/api/content-calendar/${created.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(204);
    expect(response.text).toBe('');
  });

  it('returns only active content entries when listing the calendar', async () => {
    const first = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send(validEntry)
      .expect(201);

    const second = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        ...validEntry,
        title: 'Neighborhood spotlight - East Austin',
        date: '2026-06-16T00:00:00Z',
      })
      .expect(201);

    await request(app.getHttpServer())
      .delete(`/api/content-calendar/${first.body.data.id}`)
      .set('Authorization', `Bearer ${authToken}`)
      .expect(204);

    const response = await request(app.getHttpServer())
      .get('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.data.items).toHaveLength(1);
    expect(response.body.data.items[0].id).toBe(second.body.data.id);
    expect(response.body.data.items.every((entry: { is_active: boolean }) => entry.is_active)).toBe(true);
  });
});

async function createAuthenticatedToken(app: INestApplication): Promise<string> {
  const email = uniqueEmail('calendar.user');
  const password = 'StrongPassword123!';

  await request(app.getHttpServer())
    .post('/api/auth/signup')
    .send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      password,
      terms_accepted: true,
    })
    .expect(201);

  const verificationToken = verificationTokens.get(email);
  expect(verificationToken).toBeDefined();

  await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token: verificationToken }).expect(200);

  const loginResponse = await request(app.getHttpServer())
    .post('/api/auth/login')
    .send({ email, password })
    .expect(201);

  return loginResponse.body.data.accessToken as string;
}

async function clearCalendarEntries(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('content_calendar_entries').deleteMany({});
}

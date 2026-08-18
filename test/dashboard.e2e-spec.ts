import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Dashboard (e2e)', () => {
  let app: INestApplication;
  let authToken: string;
  let userEmail: string;

  const announcementPayload = {
    announcement_title: 'Weekly market insights',
    announcement_content: 'Check the new marketing templates and neighborhood reports available this week.',
    full_name: 'Jane Doe',
    email: 'user@example.com',
    phone: '+1-555-0100',
    link: 'https://example.com/resources/market-insights',
  };

  beforeAll(async () => {
    app = await createTestApp();
    const auth = await createAuthenticatedUser(app);
    authToken = auth.token;
    userEmail = auth.email;
  });

  afterAll(async () => {
    await clearDashboardAnnouncements(app);
    await clearCalendarEntries(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearDashboardAnnouncements(app);
    await clearCalendarEntries(app);
    await resetAiCredits(app, userEmail);
  });

  it('returns 401 for dashboard overview without authentication', async () => {
    const response = await request(app.getHttpServer()).get('/api/dashboard');

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
  });

  it('returns 404 when the authenticated user has no dashboard data available', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/dashboard')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('DASHBOARD_DATA_NOT_FOUND');
  });

  it('returns 200 with dashboard overview data including announcements, content calendar, and metrics', async () => {
    await request(app.getHttpServer())
      .post('/api/dashboard/announcements')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...announcementPayload, email: userEmail })
      .expect(201);

    await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Neighborhood spotlight - East Austin',
        date: '2026-06-16T00:00:00Z',
        content: 'Highlight local coffee shops, walkability, and school access for this neighborhood.',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      })
      .expect(201);

    await request(app.getHttpServer())
      .post('/api/dashboard/questions')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ message: 'Give me a short caption for a new listing.' })
      .expect(201);

    const response = await request(app.getHttpServer())
      .get('/api/dashboard')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.data).toMatchObject({
      profile: {
        full_name: 'Jane Doe',
        email: userEmail,
      },
      announcements: [
        {
          title: announcementPayload.announcement_title,
          message: announcementPayload.announcement_content,
          status: 'active',
          error: null,
        },
      ],
      content_calendar: [
        {
          title: 'Neighborhood spotlight - East Austin',
        },
      ],
      analytics: {
        analytics_data: {
          content_generated: 1,
          current_ai_credits: 1,
        },
      },
      status: 'active',
      error: null,
    });
  });

  it('returns 200 with a list of announcements for the authenticated user', async () => {
    await request(app.getHttpServer())
      .post('/api/dashboard/announcements')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...announcementPayload, email: userEmail })
      .expect(201);

    const response = await request(app.getHttpServer())
      .get('/api/dashboard/announcements')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.data.total).toBe(1);
    expect(response.body.data.items[0]).toMatchObject({
      announcement_title: announcementPayload.announcement_title,
      announcement_content: announcementPayload.announcement_content,
      full_name: announcementPayload.full_name,
      email: userEmail,
      phone: announcementPayload.phone,
      link: announcementPayload.link,
      status: 'active',
      error: null,
    });
  });

  it('returns 401 for announcements list without authentication', async () => {
    const response = await request(app.getHttpServer()).get('/api/dashboard/announcements');

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
  });

  it('creates a new announcement and returns 201 with the created data', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/dashboard/announcements')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...announcementPayload, email: userEmail });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data).toMatchObject({
      id: expect.any(String),
      announcement_title: announcementPayload.announcement_title,
      announcement_content: announcementPayload.announcement_content,
      title: announcementPayload.announcement_title,
      message: announcementPayload.announcement_content,
      description: announcementPayload.announcement_content,
      full_name: announcementPayload.full_name,
      email: userEmail,
      phone: announcementPayload.phone,
      link: announcementPayload.link,
      status: 'active',
      error: null,
    });
  });

  it('returns 400 when the announcement email format is invalid', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/dashboard/announcements')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...announcementPayload, email: 'not-an-email' });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.email).toEqual(expect.any(Array));
  });

  it('returns 409 when a duplicate announcement title is submitted', async () => {
    await request(app.getHttpServer())
      .post('/api/dashboard/announcements')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...announcementPayload, email: userEmail })
      .expect(201);

    const response = await request(app.getHttpServer())
      .post('/api/dashboard/announcements')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ ...announcementPayload, email: userEmail });

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('ANNOUNCEMENT_TITLE_ALREADY_EXISTS');
  });

  it('returns 200 with analytics data for the authenticated user', async () => {
    await request(app.getHttpServer())
      .post('/api/dashboard/questions')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ message: 'Summarize this week in one sentence.' })
      .expect(201);

    const response = await request(app.getHttpServer())
      .get('/api/dashboard/analytics')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.data.analytics_data).toMatchObject({
      content_generated: 1,
      current_ai_credits: 1,
      total_ai_credits: 5000,
      remaining_ai_credits: 4999,
    });
  });

  it('allows a user to ask a question and receive a valid response', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/dashboard/questions')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ message: 'Write a caption for a luxury condo listing.' });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.data).toMatchObject({
      status: 'created',
      title: 'AI assistant response',
      message: expect.stringContaining('Write a caption for a luxury condo listing.'),
      credits_used: 1,
      remaining_ai_credits: 4999,
      error: null,
    });
  });

  it('returns 400 when asking a question with empty input', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/dashboard/questions')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ message: '   ' });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details.message).toEqual(expect.any(Array));
  });

  it('returns 409 when the user exceeds their AI credit limit', async () => {
    await setAiCredits(app, userEmail, { ai_credits_total: 1, ai_credits_used: 1 });

    const response = await request(app.getHttpServer())
      .post('/api/dashboard/questions')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ message: 'Create one more idea.' });

    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('AI_CREDIT_LIMIT_REACHED');
  });

  it('returns 403 when AI content generation is disabled for the user', async () => {
    await setAiCredits(app, userEmail, { ai_generation_enabled: false });

    const response = await request(app.getHttpServer())
      .post('/api/dashboard/questions')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ message: 'Create a social media hook.' });

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('AI_CONTENT_GENERATION_FORBIDDEN');
  });

  it('tracks AI credit usage and updates remaining credits accordingly', async () => {
    await setAiCredits(app, userEmail, { ai_credits_total: 5, ai_credits_used: 2 });

    await request(app.getHttpServer())
      .post('/api/dashboard/questions')
      .set('Authorization', `Bearer ${authToken}`)
      .send({ message: 'Draft a one-line neighborhood teaser.' })
      .expect(201);

    const analyticsResponse = await request(app.getHttpServer())
      .get('/api/dashboard/analytics')
      .set('Authorization', `Bearer ${authToken}`)
      .expect(200);

    expect(analyticsResponse.body.data.analytics_data).toMatchObject({
      current_ai_credits: 3,
      total_ai_credits: 5,
      remaining_ai_credits: 2,
    });
  });
});

async function createAuthenticatedUser(app: INestApplication): Promise<{ token: string; email: string }> {
  const email = uniqueEmail('dashboard.user');
  const password = 'StrongPassword123!';

  await request(app.getHttpServer())
    .post('/api/auth/signup')
    .send({
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      phone: '+1-555-0100',
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

  return {
    token: loginResponse.body.data.accessToken as string,
    email,
  };
}

async function clearDashboardAnnouncements(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('dashboard_announcements').deleteMany({});
}

async function clearCalendarEntries(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('content_calendar_entries').deleteMany({});
}

async function resetAiCredits(app: INestApplication, email: string): Promise<void> {
  await setAiCredits(app, email, {
    ai_generation_enabled: true,
    ai_credits_total: 5000,
    ai_credits_used: 0,
  });
}

async function setAiCredits(
  app: INestApplication,
  email: string,
  values: Partial<{ ai_generation_enabled: boolean; ai_credits_total: number; ai_credits_used: number }>,
): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').updateOne({ email }, { $set: values });
}

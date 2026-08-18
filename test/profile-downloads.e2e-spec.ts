import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection, Types } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Profile Downloads API (e2e)', () => {
  let app: INestApplication;
  let authToken: string;
  let userId: string;

  beforeAll(async () => {
    app = await createTestApp();
    const auth = await createAuthenticatedUser(app);
    authToken = auth.token;
    userId = auth.userId;
  });

  afterAll(async () => {
    await clearProfileDownloads(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearProfileDownloads(app);
  });

  it('returns 200 with the authenticated user download history in the expected format', async () => {
    await seedDownloads(app, userId, [
      {
        title: 'Luxury Listing Guide - 2026',
        file_type: 'PDF',
        file_size: '4.2 MB',
        last_downloaded_at: new Date('2026-06-04T09:00:00.000Z'),
        link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
        description: 'Luxury Listing Guide - 2026 (PDF, 4.2 MB)',
        is_active: true,
      },
      {
        title: 'Open House Story Pack',
        file_type: 'Image',
        file_size: '12.8 MB',
        last_downloaded_at: new Date('2026-06-02T09:00:00.000Z'),
        link: 'https://cdn.example.com/downloads/open-house-story-pack.zip',
        description: 'Open House Story Pack (Image, 12.8 MB)',
        is_active: true,
      },
      {
        title: 'Inactive Checklist',
        file_type: 'PDF',
        file_size: '1.0 MB',
        last_downloaded_at: new Date('2026-06-01T09:00:00.000Z'),
        link: 'https://cdn.example.com/downloads/inactive-checklist.pdf',
        description: 'Inactive Checklist (PDF, 1.0 MB)',
        is_active: false,
      },
    ]);

    const response = await request(app.getHttpServer())
      .get('/api/profile/downloads?page=1&limit=2')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Download history retrieved successfully');
    expect(response.body.data).toEqual({
      id: 'profile_downloads',
      title: 'Download history',
      name: 'Jane Doe',
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
      message: 'Download history retrieved successfully',
      description: 'Active download history for the authenticated user',
      profile: {
        id: userId,
        name: 'Jane Doe',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      },
      downloads: [
        {
          id: expect.any(String),
          title: 'Luxury Listing Guide - 2026',
          name: 'Luxury Listing Guide - 2026',
          file_type: 'PDF',
          file_size: '4.2 MB',
          last_downloaded: '2026-06-04',
          downloaded_at: '2026-06-04T09:00:00.000Z',
          status: 'active',
          link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
          message: 'Download available for re-download',
          description: 'Luxury Listing Guide - 2026 (PDF, 4.2 MB)',
          error: null,
        },
        {
          id: expect.any(String),
          title: 'Open House Story Pack',
          name: 'Open House Story Pack',
          file_type: 'Image',
          file_size: '12.8 MB',
          last_downloaded: '2026-06-02',
          downloaded_at: '2026-06-02T09:00:00.000Z',
          status: 'active',
          link: 'https://cdn.example.com/downloads/open-house-story-pack.zip',
          message: 'Download available for re-download',
          description: 'Open House Story Pack (Image, 12.8 MB)',
          error: null,
        },
      ],
      pagination: {
        page: 1,
        limit: 2,
        total: 2,
        total_pages: 1,
        has_next_page: false,
        has_previous_page: false,
      },
      link: null,
      error: null,
    });
  });

  it('returns 401 for download history requests without authentication', async () => {
    const response = await request(app.getHttpServer()).get('/api/profile/downloads');

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
  });

  it('triggers a re-download and returns 200 with updated metadata', async () => {
    const [downloadId] = await seedDownloads(app, userId, [
      {
        title: 'Luxury Listing Guide - 2026',
        file_type: 'PDF',
        file_size: '4.2 MB',
        last_downloaded_at: new Date('2026-06-04T09:00:00.000Z'),
        link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
        description: 'Luxury Listing Guide - 2026 (PDF, 4.2 MB)',
        is_active: true,
      },
    ]);

    const before = await getDownloadById(app, downloadId);
    expect(before?.last_downloaded_at.toISOString()).toBe('2026-06-04T09:00:00.000Z');

    const response = await request(app.getHttpServer())
      .post('/api/profile/downloads/re-download')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        download_id: downloadId,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Re-download prepared successfully');
    expect(response.body.data).toMatchObject({
      id: 'profile_download_redownload',
      title: 'Re-download ready',
      name: 'Luxury Listing Guide - 2026',
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
      message: 'Re-download prepared successfully',
      description: 'The selected file is ready to be downloaded again',
      link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
      error: null,
      download: {
        id: downloadId,
        title: 'Luxury Listing Guide - 2026',
        name: 'Luxury Listing Guide - 2026',
        file_type: 'PDF',
        file_size: '4.2 MB',
        status: 'active',
        link: 'https://cdn.example.com/downloads/luxury-listing-guide-2026.pdf',
        message: 'Download available for re-download',
        error: null,
      },
    });

    const after = await getDownloadById(app, downloadId);
    expect(after).toBeDefined();
    expect(after!.last_downloaded_at.getTime()).toBeGreaterThan(before!.last_downloaded_at.getTime());
  });

  it('returns 400 when the re-download payload is invalid', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/profile/downloads/re-download')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        download_id: 'not-an-object-id',
        full_name: ' ',
        phone: 'abc',
      });

    expect(response.status).toBe(400);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual({
      download_id: ['download_id must be a valid MongoDB ObjectId'],
      full_name: ['full_name must be between 1 and 160 characters', 'full_name is required'],
      phone: ['phone must be a valid phone number'],
    });
  });

  it('returns 404 when a user re-downloads a record that does not belong to them', async () => {
    const otherUser = await createAuthenticatedUser(app, 'profile.downloads.other');
    const [otherDownloadId] = await seedDownloads(app, otherUser.userId, [
      {
        title: 'Other User Guide',
        file_type: 'PDF',
        file_size: '5.0 MB',
        last_downloaded_at: new Date('2026-06-03T09:00:00.000Z'),
        link: 'https://cdn.example.com/downloads/other-user-guide.pdf',
        description: 'Other User Guide (PDF, 5.0 MB)',
        is_active: true,
      },
    ]);

    const response = await request(app.getHttpServer())
      .post('/api/profile/downloads/re-download')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        download_id: otherDownloadId,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });

    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('DOWNLOAD_NOT_FOUND');
  });
});

async function createAuthenticatedUser(
  app: INestApplication,
  prefix = 'profile.downloads',
): Promise<{ token: string; userId: string; email: string }> {
  const email = uniqueEmail(prefix);
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
    userId: loginResponse.body.data.id as string,
    email,
  };
}

async function clearProfileDownloads(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('profile_downloads').deleteMany({});
}

async function seedDownloads(
  app: INestApplication,
  userId: string,
  downloads: Array<{
    title: string;
    file_type: string;
    file_size: string;
    last_downloaded_at: Date;
    link: string | null;
    description: string | null;
    is_active: boolean;
  }>,
): Promise<string[]> {
  const connection = app.get<Connection>(getConnectionToken());
  const result = await connection.collection('profile_downloads').insertMany(
    downloads.map((download) => ({
      user_id: new Types.ObjectId(userId),
      ...download,
      createdAt: new Date(),
      updatedAt: new Date(),
    })),
  );

  return Object.values(result.insertedIds).map((id) => id.toString());
}

async function getDownloadById(app: INestApplication, id: string): Promise<{ last_downloaded_at: Date } | null> {
  const connection = app.get<Connection>(getConnectionToken());
  const record = await connection.collection('profile_downloads').findOne<{ last_downloaded_at: Date }>({
    _id: new Types.ObjectId(id),
  });
  return record;
}

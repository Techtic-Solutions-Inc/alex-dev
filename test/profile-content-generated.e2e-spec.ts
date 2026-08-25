import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection, Types } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Profile Content Generated API (e2e)', () => {
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
    await clearProfileContents(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearProfileContents(app);
  });

  it('returns 200 with the authenticated user generated content history', async () => {
    await seedContents(app, userId, [
      {
        title: 'Luxury Condo Social Caption',
        description: 'Fresh social caption promoting a luxury condo open house in Miami.',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
        link: null,
        is_active: true,
        createdAt: new Date('2026-08-18T09:30:00.000Z'),
        updatedAt: new Date('2026-08-18T10:15:00.000Z'),
      },
    ]);

    const response = await request(app.getHttpServer())
      .get('/api/profile/content')
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Generated content retrieved successfully');
    expect(response.body.data).toEqual({
      id: 'profile_content_generated',
      title: 'Content history',
      message: 'Generated content retrieved successfully',
      description: 'Generated content history for the authenticated user',
      name: 'Jane Doe',
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
      profile: {
        id: userId,
        name: 'Jane Doe',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      },
      contents: [
        {
          id: expect.any(String),
          content_id: expect.any(String),
          title: 'Luxury Condo Social Caption',
          description: 'Fresh social caption promoting a luxury condo open house in Miami.',
          created_at: '2026-08-18T09:30:00.000Z',
          updated_at: '2026-08-18T10:15:00.000Z',
          full_name: 'Jane Doe',
          phone: '+1-555-0100',
          profile: {
            id: userId,
            name: 'Jane Doe',
            full_name: 'Jane Doe',
            phone: '+1-555-0100',
          },
          link: null,
          error: null,
        },
      ],
      ai_credit_usage: {
        total_ai_credits: 5000,
        used_ai_credits: 0,
        remaining_ai_credits: 5000,
      },
      link: null,
      error: null,
    });
  });

  it('returns 401 when an unauthenticated user requests generated content', async () => {
    const response = await request(app.getHttpServer()).get('/api/profile/content');

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
  });

  it('creates generated content and returns 201', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/profile/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Luxury Condo Social Caption',
        description: 'Fresh social caption promoting a luxury condo open house in Miami.',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Generated content created successfully');
    expect(response.body.data).toMatchObject({
      id: expect.any(String),
      content_id: expect.any(String),
      title: 'Luxury Condo Social Caption',
      description: 'Fresh social caption promoting a luxury condo open house in Miami.',
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
      link: null,
      error: null,
    });

    const connection = app.get<Connection>(getConnectionToken());
    const contentCount = await connection.collection('profile_contents').countDocuments({ user_id: new Types.ObjectId(userId) });
    expect(contentCount).toBe(1);

    const user = await connection.collection('users').findOne<{ ai_credits_used: number }>({
      _id: new Types.ObjectId(userId),
    });
    expect(user?.ai_credits_used).toBe(1);
  });

  it('returns 400 when required create fields are missing or invalid', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/profile/content')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: ' ',
        description: ' ',
        phone: 'abc',
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('VALIDATION_ERROR');
    expect(response.body.error.details).toEqual({
      title: ['title must be between 1 and 160 characters', 'title is required'],
      description: ['description must be between 1 and 2000 characters', 'description is required'],
      full_name: [
        'full_name must be between 1 and 160 characters',
        'full_name is required',
        'full_name must be a string',
      ],
      phone: ['phone must be a valid phone number'],
    });
  });

  it('updates an existing generated content item and returns 200', async () => {
    const [contentId] = await seedContents(app, userId, [
      {
        title: 'Old Title',
        description: 'Old description.',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
        link: null,
        is_active: true,
        createdAt: new Date('2026-08-18T09:30:00.000Z'),
        updatedAt: new Date('2026-08-18T09:30:00.000Z'),
      },
    ]);

    const response = await request(app.getHttpServer())
      .put(`/api/profile/content/${contentId}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Updated Title',
        description: 'Updated description.',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
        link: 'https://agentwise.example.com/content/updated-title',
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Generated content updated successfully');
    expect(response.body.data).toMatchObject({
      id: contentId,
      content_id: contentId,
      title: 'Updated Title',
      description: 'Updated description.',
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
      link: 'https://agentwise.example.com/content/updated-title',
      error: null,
    });
  });

  it('returns 404 when updating a non-existent generated content item', async () => {
    const response = await request(app.getHttpServer())
      .put(`/api/profile/content/${new Types.ObjectId().toString()}`)
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Updated Title',
        description: 'Updated description.',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });

    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('CONTENT_NOT_FOUND');
  });

  it('deletes an existing generated content item and returns 204', async () => {
    const [contentId] = await seedContents(app, userId, [
      {
        title: 'Delete Me',
        description: 'Delete me description.',
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
        link: null,
        is_active: true,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ]);

    const response = await request(app.getHttpServer())
      .delete(`/api/profile/content/${contentId}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(204);
    expect(response.text).toBe('');

    const connection = app.get<Connection>(getConnectionToken());
    const storedRecord = await connection.collection('profile_contents').findOne<{ is_active: boolean }>({
      _id: new Types.ObjectId(contentId),
    });
    expect(storedRecord?.is_active).toBe(false);
  });

  it('returns 404 when deleting a non-existent generated content item', async () => {
    const response = await request(app.getHttpServer())
      .delete(`/api/profile/content/${new Types.ObjectId().toString()}`)
      .set('Authorization', `Bearer ${authToken}`);

    expect(response.status).toBe(404);
    expect(response.body.error.code).toBe('CONTENT_NOT_FOUND');
  });
});

async function createAuthenticatedUser(
  app: INestApplication,
  prefix = 'profile.content',
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

async function clearProfileContents(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('profile_contents').deleteMany({});
}

async function seedContents(
  app: INestApplication,
  userId: string,
  contents: Array<{
    title: string;
    description: string;
    full_name: string;
    phone: string;
    link: string | null;
    is_active: boolean;
    createdAt: Date;
    updatedAt: Date;
  }>,
): Promise<string[]> {
  const connection = app.get<Connection>(getConnectionToken());
  const result = await connection.collection('profile_contents').insertMany(
    contents.map((content) => ({
      user_id: new Types.ObjectId(userId),
      ...content,
    })),
  );

  return Object.values(result.insertedIds).map((id) => id.toString());
}

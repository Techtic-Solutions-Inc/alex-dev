import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection, Types } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Ultimate Mind AI Credits (e2e)', () => {
  let app: INestApplication;
  let agentToken: string;
  let agentEmail: string;
  let adminToken: string;
  let agentUserId: string;

  const basePath = '/api/v1/real-estate-professional/ultimate-mind/ai-credits';

  beforeAll(async () => {
    app = await createTestApp();
    const agentAuth = await createAuthenticatedUser(app, 'ultimate-mind.agent');
    agentToken = agentAuth.token;
    agentEmail = agentAuth.email;
    agentUserId = agentAuth.userId;

    const adminAuth = await createAuthenticatedUser(app, 'ultimate-mind.admin');
    adminToken = adminAuth.token;
    await setUserRole(app, adminAuth.email, 'admin');
  });

  afterAll(async () => {
    await clearUltimateMindRecords(app);
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearUltimateMindRecords(app);
    await setUserRole(app, agentEmail, 'agent');
  });

  it('returns 200 with a list of AI credit usage records on GET', async () => {
    const created = await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      })
      .expect(201);

    const response = await request(app.getHttpServer())
      .get(basePath)
      .set('Authorization', `Bearer ${agentToken}`)
      .expect(200);

    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('AI credit usage records retrieved successfully');
    expect(response.body.data.full_name).toBe('Jane Doe');
    expect(response.body.data.phone).toBe('+1-555-0100');
    expect(response.body.data.ai_credit_usage).toHaveLength(1);
    expect(response.body.data.ai_credit_usage[0]).toMatchObject({
      id: created.body.data.id,
      user: 'Jane Doe',
      usage: 1420,
      limit: 5000,
    });
  });

  it('creates a new AI credit usage record with 201 when admin POSTs valid data', async () => {
    const response = await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });

    expect(response.status).toBe(201);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('AI credit usage record created successfully');
    expect(response.body.data).toMatchObject({
      id: expect.any(String),
      user: 'Jane Doe',
      usage: 1420,
      limit: 5000,
      full_name: 'Jane Doe',
      phone: '+1-555-0100',
    });
  });

  it('updates an existing AI credit usage record with 200 when admin PUTs valid data', async () => {
    const created = await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      })
      .expect(201);

    const response = await request(app.getHttpServer())
      .put(`${basePath}/${created.body.data.id}`)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        usage: 1500,
        limit: 6000,
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('AI credit usage record updated successfully');
    expect(response.body.data).toMatchObject({
      id: created.body.data.id,
      usage: 1500,
      limit: 6000,
    });
  });

  it('returns 404 when trying to update a non-existent AI credit usage record', async () => {
    const missingId = new Types.ObjectId().toString();

    const response = await request(app.getHttpServer())
      .put(`${basePath}/${missingId}`)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({ usage: 100 });

    expect(response.status).toBe(404);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('ULTIMATE_MIND_AI_CREDIT_NOT_FOUND');
  });

  it('returns 204 when admin DELETEs an existing AI credit usage record', async () => {
    const created = await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      })
      .expect(201);

    const response = await request(app.getHttpServer())
      .delete(`${basePath}/${created.body.data.id}`)
      .set('Authorization', `Bearer ${adminToken}`);

    expect(response.status).toBe(204);
    expect(response.text).toBe('');
  });

  it('returns 403 when a non-admin user attempts to create an AI credit usage record', async () => {
    const response = await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${agentToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });

    expect(response.status).toBe(403);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('ULTIMATE_MIND_ADMIN_REQUIRED');
  });

  it('returns 403 when a non-admin user attempts to update an AI credit usage record', async () => {
    const created = await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      })
      .expect(201);

    const response = await request(app.getHttpServer())
      .put(`${basePath}/${created.body.data.id}`)
      .set('Authorization', `Bearer ${agentToken}`)
      .send({ usage: 1500 });

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ULTIMATE_MIND_ADMIN_REQUIRED');
  });

  it('returns 403 when a non-admin user attempts to delete an AI credit usage record', async () => {
    const created = await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      })
      .expect(201);

    const response = await request(app.getHttpServer())
      .delete(`${basePath}/${created.body.data.id}`)
      .set('Authorization', `Bearer ${agentToken}`);

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('ULTIMATE_MIND_ADMIN_REQUIRED');
  });

  it('returns 401 when an unauthenticated user attempts to access the endpoints', async () => {
    const response = await request(app.getHttpServer()).get(basePath);

    expect(response.status).toBe(401);
    expect(response.body.success).toBe(false);
    expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
  });

  it('syncs linked user ai_credits_used and ai_credits_total after admin create', async () => {
    await request(app.getHttpServer())
      .post(basePath)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        user_id: agentUserId,
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      })
      .expect(201);

    const connection = app.get<Connection>(getConnectionToken());
    const user = await connection.collection('users').findOne<{ ai_credits_used: number; ai_credits_total: number }>({
      _id: new Types.ObjectId(agentUserId),
    });

    expect(user?.ai_credits_used).toBe(1420);
    expect(user?.ai_credits_total).toBe(5000);
  });
});

async function createAuthenticatedUser(
  app: INestApplication,
  prefix: string,
): Promise<{ token: string; email: string; userId: string }> {
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

  const connection = app.get<Connection>(getConnectionToken());
  const user = await connection.collection('users').findOne<{ _id: Types.ObjectId }>({ email });

  return {
    token: loginResponse.body.data.accessToken as string,
    email,
    userId: user!._id.toString(),
  };
}

async function clearUltimateMindRecords(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('ultimate_mind_ai_credit_records').deleteMany({});
}

async function setUserRole(app: INestApplication, email: string, role: string): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').updateOne({ email }, { $set: { role } });
}

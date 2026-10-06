import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection, Types } from 'mongoose';
import {
  ULTIMATE_MIND_BASE_PATH,
  ULTIMATE_MIND_TEST_USERS,
  clearUltimateMindRecords,
  createUltimateMindTestContext,
  destroyUltimateMindTestContext,
  seedAiCreditRecord,
  validCreatePayload,
  type UltimateMindTestContext,
} from './fixtures/ultimate-mind.fixture';
import { uniqueEmail, verificationTokens } from './create-test-app';

describe('Ultimate Mind AI Credits Integration (e2e)', () => {
  let ctx: UltimateMindTestContext;
  let app: INestApplication;

  beforeAll(async () => {
    ctx = await createUltimateMindTestContext();
    app = ctx.app;
  });

  afterAll(async () => {
    await destroyUltimateMindTestContext(ctx);
  });

  beforeEach(async () => {
    await clearUltimateMindRecords(app);
  });

  describe('GET /ai-credits — acceptance & happy paths', () => {
    it('[JAW-9217] returns 200 with a list of AI credit usage records', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId, {
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });

      const response = await request(app.getHttpServer())
        .get(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.user.token}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('AI credit usage records retrieved successfully');
      expect(response.body.data.full_name).toBe('Regular Agent');
      expect(response.body.data.phone).toBe(ULTIMATE_MIND_TEST_USERS.user.phone);
      expect(response.body.data.ai_credit_usage).toHaveLength(1);
      expect(response.body.data.ai_credit_usage[0]).toMatchObject({
        id: created.id,
        user: 'Regular Agent',
        usage: 1420,
        limit: 5000,
      });
    });

    it('returns 200 with an empty ai_credit_usage array when the user has no records', async () => {
      const response = await request(app.getHttpServer())
        .get(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.user.token}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.ai_credit_usage).toEqual([]);
      expect(response.body.data.full_name).toBe('Regular Agent');
    });

    it('allows a viewer role to read their own AI credit usage records', async () => {
      await seedAiCreditRecord(app, ctx.admin.token, ctx.viewer.userId);

      const response = await request(app.getHttpServer())
        .get(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.viewer.token}`)
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.data.ai_credit_usage).toHaveLength(1);
    });
  });

  describe('GET /ai-credits — edge cases', () => {
    it('returns records containing unicode characters in stored full_name', async () => {
      const unicodeName = 'José García 日本語';
      await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId, { full_name: unicodeName });

      const response = await request(app.getHttpServer())
        .get(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.user.token}`)
        .expect(200);

      expect(response.body.data.ai_credit_usage[0].user).toBe('Regular Agent');
    });

    it('scopes non-admin GET results to the authenticated user only', async () => {
      await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);
      await seedAiCreditRecord(app, ctx.admin.token, ctx.viewer.userId, {
        full_name: 'Viewer Record',
        phone: '+1-555-9999',
      });

      const response = await request(app.getHttpServer())
        .get(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.user.token}`)
        .expect(200);

      expect(response.body.data.ai_credit_usage).toHaveLength(1);
      expect(response.body.data.ai_credit_usage[0].id).toBeDefined();
    });
  });

  describe('GET /ai-credits — error & auth cases', () => {
    it('returns 401 when no bearer token is provided', async () => {
      const response = await request(app.getHttpServer()).get(ULTIMATE_MIND_BASE_PATH).expect(401);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
    });

    it('returns 401 when the authenticated user account is inactive', async () => {
      const response = await request(app.getHttpServer())
        .get(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.inactive.token}`)
        .expect(401);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('INVALID_TOKEN');
    });
  });

  describe('POST /ai-credits — acceptance & happy paths', () => {
    it('[JAW-9217] creates a new AI credit usage record with 201 and valid data', async () => {
      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send(validCreatePayload(ctx.user.userId))
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('AI credit usage record created successfully');
      expect(response.body.data).toMatchObject({
        id: expect.any(String),
        user: 'Regular Agent',
        usage: 1420,
        limit: 5000,
        full_name: 'Jane Doe',
        phone: '+1-555-0100',
      });
    });
  });

  describe('POST /ai-credits — edge cases', () => {
    it('accepts full_name at the maximum allowed length of 160 characters', async () => {
      const maxName = 'A'.repeat(160);

      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send(validCreatePayload(ctx.user.userId, { full_name: maxName }))
        .expect(201);

      expect(response.body.data.full_name).toBe(maxName);
    });

    it('accepts international phone formats with spaces and parentheses', async () => {
      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send(validCreatePayload(ctx.user.userId, { phone: '+44 (20) 7946-0958' }))
        .expect(201);

      expect(response.body.data.phone).toBe('+44 (20) 7946-0958');
    });
  });

  describe('POST /ai-credits — error & auth cases', () => {
    it('returns 400 when required fields are missing from the request body', async () => {
      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send({ user_id: ctx.user.userId })
        .expect(400);

      expect(response.body.success).toBe(false);
      expect(response.body.message).toBe('Validation failed');
      expect(response.body.error.details).toEqual(
        expect.objectContaining({
          usage: expect.any(Array),
          limit: expect.any(Array),
          full_name: expect.any(Array),
          phone: expect.any(Array),
        }),
      );
    });

    it('returns 409 when an active record already exists for the linked user', async () => {
      await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send(validCreatePayload(ctx.user.userId))
        .expect(409);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('ULTIMATE_MIND_AI_CREDIT_ALREADY_EXISTS');
    });

    it('[JAW-9217] returns 403 when a non-admin user attempts to create a record', async () => {
      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.user.token}`)
        .send(validCreatePayload(ctx.user.userId))
        .expect(403);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('ULTIMATE_MIND_ADMIN_REQUIRED');
    });

    it('returns 401 when POST is attempted without authentication', async () => {
      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .send(validCreatePayload(ctx.user.userId))
        .expect(401);

      expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
    });
  });

  describe('PUT /ai-credits/:id — acceptance & happy paths', () => {
    it('[JAW-9217] updates an existing AI credit usage record with 200', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .put(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send({ usage: 1500, limit: 6000 })
        .expect(200);

      expect(response.body.success).toBe(true);
      expect(response.body.message).toBe('AI credit usage record updated successfully');
      expect(response.body.data).toMatchObject({
        id: created.id,
        usage: 1500,
        limit: 6000,
      });
    });
  });

  describe('PUT /ai-credits/:id — edge cases', () => {
    it('supports partial updates to full_name and phone Figma fields', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .put(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send({ full_name: 'Updated Name', phone: '+1-555-0199' })
        .expect(200);

      expect(response.body.data.full_name).toBe('Updated Name');
      expect(response.body.data.phone).toBe('+1-555-0199');
    });

    it('accepts boundary values usage=0 and limit=1', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .put(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send({ usage: 0, limit: 1 })
        .expect(200);

      expect(response.body.data.usage).toBe(0);
      expect(response.body.data.limit).toBe(1);
    });
  });

  describe('PUT /ai-credits/:id — error & auth cases', () => {
    it('[JAW-9217] returns 404 when updating a non-existent AI credit usage record', async () => {
      const missingId = new Types.ObjectId().toString();

      const response = await request(app.getHttpServer())
        .put(`${ULTIMATE_MIND_BASE_PATH}/${missingId}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send({ usage: 100 })
        .expect(404);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('ULTIMATE_MIND_AI_CREDIT_NOT_FOUND');
    });

    it('returns 422 when usage exceeds the credit limit', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .put(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send({ usage: 9999, limit: 100 })
        .expect(422);

      expect(response.body.success).toBe(false);
      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    });

    it('returns 403 when a viewer attempts to update a record', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .put(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.viewer.token}`)
        .send({ usage: 1500 })
        .expect(403);

      expect(response.body.error.code).toBe('ULTIMATE_MIND_ADMIN_REQUIRED');
    });

    it('returns 401 when PUT is attempted without authentication', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .put(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .send({ usage: 1500 })
        .expect(401);

      expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
    });
  });

  describe('DELETE /ai-credits/:id — acceptance & happy paths', () => {
    it('[JAW-9217] returns 204 when deleting an existing AI credit usage record', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .delete(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .expect(204);

      expect(response.text).toBe('');

      const listResponse = await request(app.getHttpServer())
        .get(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.user.token}`)
        .expect(200);

      expect(listResponse.body.data.ai_credit_usage).toHaveLength(0);
    });
  });

  describe('DELETE /ai-credits/:id — edge cases', () => {
    it('returns 404 when deleting a record that was already soft-deleted', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      await request(app.getHttpServer())
        .delete(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .expect(204);

      const response = await request(app.getHttpServer())
        .delete(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .expect(404);

      expect(response.body.error.code).toBe('ULTIMATE_MIND_AI_CREDIT_NOT_FOUND');
    });

    it('returns 404 when the record id is not a valid MongoDB ObjectId', async () => {
      const response = await request(app.getHttpServer())
        .delete(`${ULTIMATE_MIND_BASE_PATH}/not-a-valid-object-id`)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .expect(404);

      expect(response.body.error.code).toBe('ULTIMATE_MIND_AI_CREDIT_NOT_FOUND');
    });
  });

  describe('DELETE /ai-credits/:id — error & auth cases', () => {
    it('returns 403 when a regular user attempts to delete a record', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .delete(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .set('Authorization', `Bearer ${ctx.user.token}`)
        .expect(403);

      expect(response.body.error.code).toBe('ULTIMATE_MIND_ADMIN_REQUIRED');
    });

    it('returns 401 when DELETE is attempted without authentication', async () => {
      const created = await seedAiCreditRecord(app, ctx.admin.token, ctx.user.userId);

      const response = await request(app.getHttpServer())
        .delete(`${ULTIMATE_MIND_BASE_PATH}/${created.id}`)
        .expect(401);

      expect(response.body.error.code).toBe('AUTHENTICATION_REQUIRED');
    });
  });

  describe('Data integrity & registration', () => {
    it('returns 404 when creating a record for a deactivated linked user', async () => {
      const response = await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send(validCreatePayload(ctx.inactive.userId))
        .expect(404);

      expect(response.body.error.code).toBe('USER_NOT_FOUND');
    });

    it('syncs linked user ai_credits_used and ai_credits_total after admin create', async () => {
      await request(app.getHttpServer())
        .post(ULTIMATE_MIND_BASE_PATH)
        .set('Authorization', `Bearer ${ctx.admin.token}`)
        .send(validCreatePayload(ctx.user.userId, { usage: 2000, limit: 8000 }))
        .expect(201);

      const connection = app.get<Connection>(getConnectionToken());
      const user = await connection.collection('users').findOne<{ ai_credits_used: number; ai_credits_total: number }>({
        _id: new Types.ObjectId(ctx.user.userId),
      });

      expect(user?.ai_credits_used).toBe(2000);
      expect(user?.ai_credits_total).toBe(8000);
    });

    it('registers a new user via signup using the new-user fixture payload', async () => {
      const signupEmail = uniqueEmail('ultimate-mind.newuser');

      const response = await request(app.getHttpServer())
        .post('/api/auth/signup')
        .send({
          first_name: ULTIMATE_MIND_TEST_USERS.newUser.first_name,
          last_name: ULTIMATE_MIND_TEST_USERS.newUser.last_name,
          email: signupEmail,
          phone: ULTIMATE_MIND_TEST_USERS.newUser.phone,
          password: ULTIMATE_MIND_TEST_USERS.newUser.password,
          terms_accepted: ULTIMATE_MIND_TEST_USERS.newUser.terms_accepted,
        })
        .expect(201);

      expect(response.body.success).toBe(true);
      expect(verificationTokens.has(signupEmail)).toBe(true);
    });
  });
});

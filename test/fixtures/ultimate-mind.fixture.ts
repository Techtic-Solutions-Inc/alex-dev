import { INestApplication } from '@nestjs/common';
import { getConnectionToken } from '@nestjs/mongoose';
import request = require('supertest');
import { Connection, Types } from 'mongoose';
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from '../create-test-app';

export const ULTIMATE_MIND_BASE_PATH = '/api/v1/real-estate-professional/ultimate-mind/ai-credits';

/** Canonical test user definitions for Ultimate Mind integration tests. */
export const ULTIMATE_MIND_TEST_USERS = {
  admin: {
    emailPrefix: 'ultimate-mind.admin',
    role: 'admin',
    password: 'TestAdmin123!',
    first_name: 'Admin',
    last_name: 'User',
    phone: '+1-555-0101',
  },
  user: {
    emailPrefix: 'ultimate-mind.user',
    role: 'agent',
    password: 'TestUser123!',
    first_name: 'Regular',
    last_name: 'Agent',
    phone: '+1-555-0102',
  },
  viewer: {
    emailPrefix: 'ultimate-mind.viewer',
    role: 'viewer',
    password: 'TestViewer123!',
    first_name: 'Read',
    last_name: 'Only',
    phone: '+1-555-0103',
  },
  inactive: {
    emailPrefix: 'ultimate-mind.inactive',
    role: 'agent',
    password: 'InactiveUser123!',
    first_name: 'Inactive',
    last_name: 'Account',
    phone: '+1-555-0104',
    is_active: false,
  },
  newUser: {
    email: 'newuser@test.com',
    role: 'agent',
    password: 'NewUser123!',
    first_name: 'New',
    last_name: 'Signup',
    phone: '+1-555-0105',
    terms_accepted: true,
  },
} as const;

export type AuthenticatedTestUser = {
  token: string;
  email: string;
  userId: string;
  role: string;
};

export type UltimateMindTestContext = {
  app: INestApplication;
  admin: AuthenticatedTestUser;
  user: AuthenticatedTestUser;
  viewer: AuthenticatedTestUser;
  inactive: AuthenticatedTestUser;
};

/**
 * Boots the NestJS application and inserts five test users with distinct roles and states.
 * Email delivery is mocked via createTestApp's EmailVerificationService override.
 */
export async function createUltimateMindTestContext(): Promise<UltimateMindTestContext> {
  const app = await createTestApp();

  const admin = await createAuthenticatedTestUser(app, ULTIMATE_MIND_TEST_USERS.admin);
  await setUserRole(app, admin.email, 'admin');

  const user = await createAuthenticatedTestUser(app, ULTIMATE_MIND_TEST_USERS.user);
  const viewer = await createAuthenticatedTestUser(app, ULTIMATE_MIND_TEST_USERS.viewer);
  await setUserRole(app, viewer.email, 'viewer');

  const inactive = await createAuthenticatedTestUser(app, ULTIMATE_MIND_TEST_USERS.inactive);
  await setUserActive(app, inactive.email, false);

  return { app, admin, user, viewer, inactive };
}

/**
 * Creates a verified, logged-in user and optionally applies role/active overrides.
 */
export async function createAuthenticatedTestUser(
  app: INestApplication,
  profile: {
    emailPrefix?: string;
    email?: string;
    password: string;
    first_name: string;
    last_name: string;
    phone: string;
    role?: string;
    is_active?: boolean;
  },
): Promise<AuthenticatedTestUser> {
  const email = profile.email ?? uniqueEmail(profile.emailPrefix ?? 'ultimate-mind.test');
  const password = profile.password;

  await request(app.getHttpServer())
    .post('/api/auth/signup')
    .send({
      first_name: profile.first_name,
      last_name: profile.last_name,
      email,
      phone: profile.phone,
      password,
      terms_accepted: true,
    })
    .expect(201);

  const verificationToken = verificationTokens.get(email);
  if (!verificationToken) {
    throw new Error(`Missing verification token for ${email}`);
  }

  await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token: verificationToken }).expect(200);

  const loginResponse = await request(app.getHttpServer())
    .post('/api/auth/login')
    .send({ email, password })
    .expect(201);

  const connection = app.get<Connection>(getConnectionToken());
  const user = await connection.collection('users').findOne<{ _id: Types.ObjectId; role?: string }>({ email });

  if (!user) {
    throw new Error(`User document missing after signup for ${email}`);
  }

  if (profile.role) {
    await setUserRole(app, email, profile.role);
  }

  if (profile.is_active === false) {
    await setUserActive(app, email, false);
  }

  return {
    token: loginResponse.body.data.accessToken as string,
    email,
    userId: user._id.toString(),
    role: profile.role ?? user.role ?? 'agent',
  };
}

/** Removes all Ultimate Mind AI credit records from the test database. */
export async function clearUltimateMindRecords(app: INestApplication): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('ultimate_mind_ai_credit_records').deleteMany({});
}

/** Sets the role field on a user document. */
export async function setUserRole(app: INestApplication, email: string, role: string): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').updateOne({ email }, { $set: { role } });
}

/** Activates or deactivates a user account. */
export async function setUserActive(app: INestApplication, email: string, isActive: boolean): Promise<void> {
  const connection = app.get<Connection>(getConnectionToken());
  await connection.collection('users').updateOne({ email }, { $set: { is_active: isActive } });
}

/** Standard valid payload for creating an Ultimate Mind AI credit record. */
export function validCreatePayload(userId: string, overrides: Record<string, unknown> = {}): Record<string, unknown> {
  return {
    user_id: userId,
    usage: 1420,
    limit: 5000,
    full_name: 'Jane Doe',
    phone: '+1-555-0100',
    ...overrides,
  };
}

/** Creates a record via admin API and returns the response body data. */
export async function seedAiCreditRecord(
  app: INestApplication,
  adminToken: string,
  userId: string,
  overrides: Record<string, unknown> = {},
): Promise<{ id: string; user: string; usage: number; limit: number }> {
  const response = await request(app.getHttpServer())
    .post(ULTIMATE_MIND_BASE_PATH)
    .set('Authorization', `Bearer ${adminToken}`)
    .send(validCreatePayload(userId, overrides))
    .expect(201);

  return response.body.data;
}

/** Tears down Ultimate Mind test data and closes the application. */
export async function destroyUltimateMindTestContext(context: UltimateMindTestContext): Promise<void> {
  await clearUltimateMindRecords(context.app);
  await clearUsers(context.app);
  await context.app.close();
}

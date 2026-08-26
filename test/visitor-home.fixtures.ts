import { INestApplication } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { getConnectionToken } from '@nestjs/mongoose';
import { Connection } from 'mongoose';
import request = require('supertest');
import { uniqueEmail, verificationTokens } from './create-test-app';

export interface VisitorHomePersona {
  email: string;
  password: string;
  role: 'admin' | 'agent' | 'marketing_manager';
  is_active: boolean;
  first_name: string;
  last_name: string;
  inserted: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  userId: string | null;
}

export interface VisitorHomePersonas {
  admin: VisitorHomePersona;
  user: VisitorHomePersona;
  viewer: VisitorHomePersona;
  inactive: VisitorHomePersona;
  new: VisitorHomePersona;
}

export const VISITOR_HOME_CONTENT_SEED = {
  title: 'Luxury Listing Social Template',
  description: 'Help real estate professionals create content faster with ready-made templates.',
  category: 'Social Media',
  tags: ['templates', 'instagram', 'listing'],
  image_url: 'https://cdn.example.com/visitor/home/luxury-listing-template.jpg',
  link: 'https://example.com/visitor/home/luxury-listing-template',
  is_active: true,
};

/**
 * Mocks Google Analytics Measurement Protocol and Auth0 token calls so e2e tests never hit the network.
 * DATABASE_URL is read from .env.test via test/setup-env.ts — never hardcoded here.
 */
export function installThirdPartyMocks(): jest.SpyInstance {
  process.env.GOOGLE_ANALYTICS_MEASUREMENT_ID = 'G-TEST';
  process.env.GOOGLE_ANALYTICS_API_SECRET = 'test-ga-secret';
  process.env.AUTH0_DOMAIN = '';
  process.env.AUTH0_CLIENT_ID = '';
  process.env.AUTH0_CLIENT_SECRET = '';
  process.env.AUTH0_CONNECTION = '';

  return jest.spyOn(global, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.includes('google-analytics.com/mp/collect')) {
      return { ok: true, status: 200, json: async () => ({}) } as Response;
    }
    if (url.includes('/oauth/token')) {
      return {
        ok: true,
        status: 200,
        json: async () => ({ access_token: 'mock-auth0-access-token', token_type: 'Bearer' }),
      } as Response;
    }
    throw new Error(`Unexpected third-party fetch in visitor home tests: ${url}`);
  });
}

/**
 * Inserts one public visitor Home content document and returns its id.
 */
export async function seedVisitorHomeContent(
  app: INestApplication,
  overrides: Record<string, unknown> = {},
): Promise<string> {
  const connection = app.get<Connection>(getConnectionToken());
  const inserted = await connection.collection('visitor_home_contents').insertOne({
    ...VISITOR_HOME_CONTENT_SEED,
    createdAt: new Date('2026-06-01T10:00:00.000Z'),
    updatedAt: new Date('2026-06-02T12:30:00.000Z'),
    ...overrides,
  });
  return inserted.insertedId.toString();
}

/**
 * Registers, verifies, and logs in a user through the real auth API (SendGrid is mocked in createTestApp).
 */
export async function registerVerifiedUser(
  app: INestApplication,
  email: string,
  password: string,
  firstName: string,
  lastName: string,
): Promise<{ userId: string; accessToken: string; refreshToken: string }> {
  const signup = await request(app.getHttpServer()).post('/api/auth/signup').send({
    first_name: firstName,
    last_name: lastName,
    email,
    password,
    terms_accepted: true,
  });
  if (signup.status !== 201) {
    throw new Error(`signup failed for ${email}: ${signup.status} ${JSON.stringify(signup.body)}`);
  }

  const verificationToken = verificationTokens.get(email);
  if (!verificationToken) {
    throw new Error(`verification token missing for ${email}`);
  }
  await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token: verificationToken }).expect(200);

  const login = await request(app.getHttpServer()).post('/api/auth/login').send({ email, password });
  if (login.status !== 201) {
    throw new Error(`login failed for ${email}: ${login.status} ${JSON.stringify(login.body)}`);
  }

  return {
    userId: login.body.data.id as string,
    accessToken: login.body.data.accessToken as string,
    refreshToken: login.body.data.refreshToken as string,
  };
}

/**
 * Inserts admin, agent, marketing_manager (viewer analogue), and inactive users.
 * The "new" persona is intentionally not written to the users collection.
 * This schema has no viewer role; marketing_manager is the closest read-oriented role.
 */
export async function seedVisitorHomePersonas(app: INestApplication): Promise<VisitorHomePersonas> {
  const connection = app.get<Connection>(getConnectionToken());

  const adminEmail = uniqueEmail('admin.test');
  const userEmail = uniqueEmail('user.test');
  const viewerEmail = uniqueEmail('viewer.test');
  const inactiveEmail = uniqueEmail('inactive.test');
  const newEmail = uniqueEmail('newuser.test');

  const adminAuth = await registerVerifiedUser(app, adminEmail, 'TestAdmin123!', 'Ada', 'Admin');
  await connection.collection('users').updateOne({ email: adminEmail }, { $set: { role: 'admin' } });

  const userAuth = await registerVerifiedUser(app, userEmail, 'TestUser123!', 'Riley', 'Agent');

  const viewerAuth = await registerVerifiedUser(app, viewerEmail, 'TestViewer123!', 'Vera', 'Viewer');
  await connection.collection('users').updateOne({ email: viewerEmail }, { $set: { role: 'marketing_manager' } });

  const inactiveAuth = await registerVerifiedUser(app, inactiveEmail, 'TestInactive123!', 'Ivan', 'Inactive');
  await connection.collection('users').updateOne({ email: inactiveEmail }, { $set: { is_active: false } });

  return {
    admin: {
      email: adminEmail,
      password: 'TestAdmin123!',
      role: 'admin',
      is_active: true,
      first_name: 'Ada',
      last_name: 'Admin',
      inserted: true,
      accessToken: adminAuth.accessToken,
      refreshToken: adminAuth.refreshToken,
      userId: adminAuth.userId,
    },
    user: {
      email: userEmail,
      password: 'TestUser123!',
      role: 'agent',
      is_active: true,
      first_name: 'Riley',
      last_name: 'Agent',
      inserted: true,
      accessToken: userAuth.accessToken,
      refreshToken: userAuth.refreshToken,
      userId: userAuth.userId,
    },
    viewer: {
      email: viewerEmail,
      password: 'TestViewer123!',
      role: 'marketing_manager',
      is_active: true,
      first_name: 'Vera',
      last_name: 'Viewer',
      inserted: true,
      accessToken: viewerAuth.accessToken,
      refreshToken: viewerAuth.refreshToken,
      userId: viewerAuth.userId,
    },
    inactive: {
      email: inactiveEmail,
      password: 'TestInactive123!',
      role: 'agent',
      is_active: false,
      first_name: 'Ivan',
      last_name: 'Inactive',
      inserted: true,
      accessToken: inactiveAuth.accessToken,
      refreshToken: inactiveAuth.refreshToken,
      userId: inactiveAuth.userId,
    },
    new: {
      email: newEmail,
      password: 'NewUser123!',
      role: 'agent',
      is_active: true,
      first_name: 'Nora',
      last_name: 'New',
      inserted: false,
      accessToken: null,
      refreshToken: null,
      userId: null,
    },
  };
}

/**
 * Issues an expired access token for auth-negative cases on protected routes.
 */
export function issueExpiredAccessToken(app: INestApplication, userId: string): string {
  const jwtService = app.get(JwtService);
  return jwtService.sign({ sub: userId, tokenUse: 'access' }, { expiresIn: 0 });
}

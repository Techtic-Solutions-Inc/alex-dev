import { INestApplication } from '@nestjs/common';
import request = require('supertest');
import { clearUsers, createTestApp, uniqueEmail, verificationTokens } from './create-test-app';

describe('Profile API (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    app = await createTestApp();
  });

  afterAll(async () => {
    await clearUsers(app);
    await app.close();
  });

  beforeEach(async () => {
    await clearUsers(app);
  });

  async function registerAndLogin(email: string, password = 'StrongPassword123!'): Promise<string> {
    await request(app.getHttpServer())
      .post('/api/auth/signup')
      .send({
        first_name: 'Joseph',
        last_name: 'Stanley',
        email,
        password,
        terms_accepted: true,
      })
      .expect(201);

    const verificationToken = verificationTokens.get(email);
    expect(verificationToken).toBeDefined();

    await request(app.getHttpServer()).get('/api/auth/verify-email').query({ token: verificationToken }).expect(200);

    const loginResponse = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password,
    });

    expect(loginResponse.status).toBe(201);
    return loginResponse.body.data.accessToken as string;
  }

  it('returns the authenticated user profile', async () => {
    const email = uniqueEmail('profile.get');
    const token = await registerAndLogin(email);

    const updateResponse = await request(app.getHttpServer())
      .put('/api/profile')
      .set('Authorization', `Bearer ${token}`)
      .send({
        first_name: 'Joseph',
        last_name: 'Stanley',
        email,
        mobile_number: '123-456-7890',
        phone: '+1-555-0100',
        bio: 'How you show up across the studio.',
        time_zone: 'Washington, DC, USA (GMT-4)',
        street: '123 Main St',
        country: 'USA',
        state: 'DC',
        city: 'Washington',
        zip: '20001',
      });

    expect(updateResponse.status).toBe(200);

    const response = await request(app.getHttpServer()).get('/api/profile').set('Authorization', `Bearer ${token}`);

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Profile retrieved successfully');
    expect(response.body.data).toEqual({
      id: expect.any(String),
      name: 'Joseph Stanley',
      full_name: 'Joseph Stanley',
      first_name: 'Joseph',
      last_name: 'Stanley',
      email,
      mobile_number: '123-456-7890',
      phone: '+1-555-0100',
      bio: 'How you show up across the studio.',
      description: 'How you show up across the studio.',
      time_zone: 'Washington, DC, USA (GMT-4)',
      street: '123 Main St',
      country: 'USA',
      state: 'DC',
      city: 'Washington',
      zip: '20001',
      address: '123 Main St, Washington, DC, 20001, USA',
      profile: {
        bio: 'How you show up across the studio.',
        description: 'How you show up across the studio.',
        image: null,
        name: 'Joseph Stanley',
      },
      address_details: {
        street: '123 Main St',
        city: 'Washington',
        state: 'DC',
        zip: '20001',
        country: 'USA',
      },
      image: null,
      password: null,
      link: null,
      error: null,
    });
  });

  it('updates the authenticated user profile', async () => {
    const email = uniqueEmail('profile.update');
    const token = await registerAndLogin(email);

    const response = await request(app.getHttpServer())
      .put('/api/profile')
      .set('Authorization', `Bearer ${token}`)
      .send({
        first_name: 'Jane',
        last_name: 'Doe',
        email,
        mobile_number: '123-456-7890',
        phone: '+1-555-0100',
        bio: 'How you show up across the studio.',
        time_zone: 'Washington, DC, USA (GMT-4)',
        street: '123 Main St',
        country: 'USA',
        state: 'DC',
        city: 'Washington',
        zip: '20001',
      });

    expect(response.status).toBe(200);
    expect(response.body.success).toBe(true);
    expect(response.body.message).toBe('Profile updated successfully');
    expect(response.body.data).toMatchObject({
      name: 'Jane Doe',
      full_name: 'Jane Doe',
      first_name: 'Jane',
      last_name: 'Doe',
      email,
      mobile_number: '123-456-7890',
      phone: '+1-555-0100',
      city: 'Washington',
      country: 'USA',
      zip: '20001',
      bio: 'How you show up across the studio.',
    });
  });

  it('returns validation error for an invalid email format', async () => {
    const token = await registerAndLogin(uniqueEmail('profile.invalid-email'));

    const response = await request(app.getHttpServer())
      .put('/api/profile')
      .set('Authorization', `Bearer ${token}`)
      .send({
        first_name: 'Joseph',
        last_name: 'Stanley',
        email: 'invalid-email',
      });

    expect(response.status).toBe(400);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Validation failed');
    expect(response.body.error).toEqual({
      code: 'VALIDATION_ERROR',
      details: {
        email: ['email must be a valid email address'],
      },
    });
  });

  it('changes the password with the correct current password', async () => {
    const email = uniqueEmail('profile.password');
    const token = await registerAndLogin(email);

    const response = await request(app.getHttpServer())
      .post('/api/profile/change-password')
      .set('Authorization', `Bearer ${token}`)
      .send({
        current_password: 'StrongPassword123!',
        new_password: 'NewStrongPassword456!',
        confirm_password: 'NewStrongPassword456!',
      });

    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      success: true,
      message: 'Password changed successfully',
      data: {},
    });

    const oldPasswordLogin = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password: 'StrongPassword123!',
    });

    expect(oldPasswordLogin.status).toBe(401);
    expect(oldPasswordLogin.body.error.code).toBe('INVALID_CREDENTIALS');

    const newPasswordLogin = await request(app.getHttpServer()).post('/api/auth/login').send({
      email,
      password: 'NewStrongPassword456!',
    });

    expect(newPasswordLogin.status).toBe(201);
    expect(newPasswordLogin.body.success).toBe(true);
  });

  it('returns conflict when updating to a duplicate email', async () => {
    const existingEmail = uniqueEmail('profile.duplicate.existing');
    await registerAndLogin(existingEmail);

    const currentEmail = uniqueEmail('profile.duplicate.current');
    const token = await registerAndLogin(currentEmail);

    const response = await request(app.getHttpServer())
      .put('/api/profile')
      .set('Authorization', `Bearer ${token}`)
      .send({
        first_name: 'Joseph',
        last_name: 'Stanley',
        email: existingEmail,
      });

    expect(response.status).toBe(409);
    expect(response.body.success).toBe(false);
    expect(response.body.message).toBe('Another account already uses this email address');
    expect(response.body.error).toEqual({
      code: 'EMAIL_ALREADY_EXISTS',
      details: {
        email: ['Another account already uses this email address'],
      },
    });
  });
});

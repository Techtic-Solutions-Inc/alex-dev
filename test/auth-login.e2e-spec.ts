import request from 'supertest';
import { Test } from '@nestjs/testing';
import { AppModule } from '../src/app.module';
import { INestApplication } from '@nestjs/common';
import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';

describe('Auth Login', () => {
  let app: INestApplication;
  let mongoServer: MongoMemoryServer;

  beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    await mongoose.connect(uri);

    const moduleRef = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleRef.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await mongoose.disconnect();
    await mongoServer.stop();
    await app.close();
  });

  it('should return 201 and a valid JWT token on successful login', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'user@test.com', password: 'TestUser123!' });

    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('token');
    expect(response.body.token).toMatch(/^eyJhbGciOiJIUzI1NiJ9/);
  });

  it('should return 400 for empty email', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: '', password: 'TestUser123!' });

    expect(response.status).toBe(400);
    expect(response.body.message).toContain('email must not be empty');
  });

  it('should return 400 for empty password', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'user@test.com', password: '' });

    expect(response.status).toBe(400);
    expect(response.body.message).toContain('password must not be empty');
  });

  it('should return 404 for unregistered email', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'unregistered@test.com', password: 'TestUser123!' });

    expect(response.status).toBe(404);
    expect(response.body.message).toContain('User not found');
  });

  it('should return 401 for incorrect password', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'user@test.com', password: 'WrongPassword!' });

    expect(response.status).toBe(401);
    expect(response.body.message).toContain('Invalid credentials');
  });

  it('should return 403 for inactive user', async () => {
    const response = await request(app)
      .post('/api/auth/login')
      .send({ email: 'inactive@test.com', password: 'TestUser123!' });

    expect(response.status).toBe(403);
    expect(response.body.message).toContain('User account is inactive');
  });

  it('should return 401 for missing token on logout', async () => {
    const response = await request(app)
      .get('/api/auth/logout');

    expect(response.status).toBe(401);
    expect(response.body.message).toContain('Unauthorized');
  });
});
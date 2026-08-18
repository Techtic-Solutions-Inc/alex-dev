import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { setupTestDB } from './setup-env';

let app: INestApplication;

beforeAll(async () => {
  const moduleFixture: TestingModule = await Test.createTestingModule({
    imports: [AppModule],
  }).compile();

  app = moduleFixture.createNestApplication();
  await app.init();
  await setupTestDB();
});

afterAll(async () => {
  await app.close();
});

describe('Content Calendar API (e2e)', () => {
  it('should create a new content entry with valid data', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        title: 'Market update — Austin Q2',
        date: '2026-06-15T00:00:00Z',
        content: 'Your personal content calendar...',
        full_name: 'Jane Doe',
        phone: '+1-555-0100'
      });
    expect(response.status).toBe(201);
    expect(response.body).toHaveProperty('id');
  });

  it('should return 400 for missing required fields', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        date: '2026-06-15T00:00:00Z',
        content: 'Your personal content calendar...'
      });
    expect(response.status).toBe(400);
  });

  it('should return 409 for duplicate title on the same date', async () => {
    await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        title: 'Market update — Austin Q2',
        date: '2026-06-15T00:00:00Z',
        content: 'Your personal content calendar...',
        full_name: 'Jane Doe',
        phone: '+1-555-0100'
      });

    const response = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        title: 'Market update — Austin Q2',
        date: '2026-06-15T00:00:00Z',
        content: 'Another content entry...',
        full_name: 'Jane Doe',
        phone: '+1-555-0100'
      });
    expect(response.status).toBe(409);
  });

  it('should update an existing content entry', async () => {
    const createResponse = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        title: 'Market update — Austin Q2',
        date: '2026-06-15T00:00:00Z',
        content: 'Your personal content calendar...',
        full_name: 'Jane Doe',
        phone: '+1-555-0100'
      });

    const updateResponse = await request(app.getHttpServer())
      .put(`/api/content-calendar/${createResponse.body.id}`)
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        title: 'Updated Market update — Austin Q2',
        content: 'Updated content...'
      });
    expect(updateResponse.status).toBe(200);
    expect(updateResponse.body.title).toBe('Updated Market update — Austin Q2');
  });

  it('should return 404 for updating non-existent content entry', async () => {
    const response = await request(app.getHttpServer())
      .put('/api/content-calendar/invalid-id')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        title: 'Non-existent update',
        content: 'Non-existent content...'
      });
    expect(response.status).toBe(404);
  });

  it('should delete a content entry', async () => {
    const createResponse = await request(app.getHttpServer())
      .post('/api/content-calendar')
      .set('Authorization', `Bearer ${adminToken}`)
      .send({
        title: 'Market update — Austin Q2',
        date: '2026-06-15T00:00:00Z',
        content: 'Your personal content calendar...',
        full_name: 'Jane Doe',
        phone: '+1-555-0100'
      });

    const deleteResponse = await request(app.getHttpServer())
      .delete(`/api/content-calendar/${createResponse.body.id}`)
      .set('Authorization', `Bearer ${adminToken}`);
    expect(deleteResponse.status).toBe(204);
  });

  it('should return only active content entries', async () => {
    const response = await request(app.getHttpServer())
      .get('/api/content-calendar')
      .set('Authorization', `Bearer ${adminToken}`);
    expect(response.status).toBe(200);
    expect(response.body.every(entry => entry.isActive)).toBe(true);
  });
});
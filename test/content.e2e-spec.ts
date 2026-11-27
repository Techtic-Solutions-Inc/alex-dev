import request from 'supertest';
import { Test } from '@nestjs/testing';
import { AppModule } from '../src/app.module';
import { INestApplication } from '@nestjs/common';
import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';

describe('Content API', () => {
    let app: INestApplication;
    let mongoServer: MongoMemoryServer;

    beforeAll(async () => {
        mongoServer = await MongoMemoryServer.create();
        const uri = mongoServer.getUri();
        process.env.DATABASE_URL = uri;

        const moduleFixture = await Test.createTestingModule({
            imports: [AppModule],
        }).compile();

        app = moduleFixture.createNestApplication();
        await app.init();
    });

    afterAll(async () => {
        await app.close();
        await mongoServer.stop();
        await mongoose.disconnect();
    });

    it('GET /api/content should return a list of content items', async () => {
        const response = await request(app.getHttpServer()).get('/api/content');
        expect(response.status).toBe(200);
        expect(Array.isArray(response.body)).toBe(true);
    });

    it('POST /api/content should create a new content item', async () => {
        const newItem = { title: 'Test Content', description: 'Test Description', image_url: 'http://example.com/image.png', tags: ['tag1'], phone: '+1-555-0100', terms_accepted: true };
        const response = await request(app.getHttpServer()).post('/api/content').send(newItem);
        expect(response.status).toBe(201);
        expect(response.body.title).toBe(newItem.title);
    });

    it('PUT /api/content/:id should update an existing content item', async () => {
        const newItem = { title: 'Test Content', description: 'Test Description', image_url: 'http://example.com/image.png', tags: ['tag1'], phone: '+1-555-0100', terms_accepted: true };
        const createResponse = await request(app.getHttpServer()).post('/api/content').send(newItem);
        const itemId = createResponse.body.id;

        const updatedItem = { title: 'Updated Content' };
        const response = await request(app.getHttpServer()).put(`/api/content/${itemId}`).send(updatedItem);
        expect(response.status).toBe(200);
        expect(response.body.title).toBe(updatedItem.title);
    });

    it('DELETE /api/content/:id should delete a content item', async () => {
        const newItem = { title: 'Test Content', description: 'Test Description', image_url: 'http://example.com/image.png', tags: ['tag1'], phone: '+1-555-0100', terms_accepted: true };
        const createResponse = await request(app.getHttpServer()).post('/api/content').send(newItem);
        const itemId = createResponse.body.id;

        const response = await request(app.getHttpServer()).delete(`/api/content/${itemId}`);
        expect(response.status).toBe(204);
    });

    it('GET /api/content with empty search term should return 400', async () => {
        const response = await request(app.getHttpServer()).get('/api/content?search=');
        expect(response.status).toBe(400);
        expect(response.body.message).toBe('Search term cannot be empty');
    });

    it('POST /api/content with duplicate title should return 409', async () => {
        const newItem = { title: 'Duplicate Title', description: 'Test Description', image_url: 'http://example.com/image.png', tags: ['tag1'], phone: '+1-555-0100', terms_accepted: true };
        await request(app.getHttpServer()).post('/api/content').send(newItem);
        const response = await request(app.getHttpServer()).post('/api/content').send(newItem);
        expect(response.status).toBe(409);
        expect(response.body.message).toBe('Content item with this title already exists');
    });

    it('POST /api/content without terms accepted should return 400', async () => {
        const newItem = { title: 'Test Content', description: 'Test Description', image_url: 'http://example.com/image.png', tags: ['tag1'], phone: '+1-555-0100' };
        const response = await request(app.getHttpServer()).post('/api/content').send(newItem);
        expect(response.status).toBe(400);
        expect(response.body.message).toBe('Terms must be accepted');
    });
});
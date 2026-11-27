import request from 'supertest';
import { Test } from '@nestjs/testing';
import { AppModule } from '../src/app.module';
import { INestApplication } from '@nestjs/common';
import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';

describe('Database Migrations', () => {
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

    it('should run initial migration', async () => {
        const response = await request(app.getHttpServer()).post('/api/migrate');
        expect(response.status).toBe(200);
        expect(response.body).toEqual({ message: 'Migration completed successfully' });
    });

    it('should rollback the last migration', async () => {
        const response = await request(app.getHttpServer()).post('/api/migrate/rollback');
        expect(response.status).toBe(200);
        expect(response.body).toEqual({ message: 'Rollback completed successfully' });
    });
});
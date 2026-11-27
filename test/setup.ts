import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';
import { Test, TestingModule } from '@nestjs/testing';
import { AppModule } from '../src/app.module';
import request from 'supertest';

let mongoServer: MongoMemoryServer;
let app;

beforeAll(async () => {
    mongoServer = await MongoMemoryServer.create();
    const uri = mongoServer.getUri();
    process.env.DATABASE_URL = uri;

    const moduleFixture: TestingModule = await Test.createTestingModule({
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

export const createUser = async (userData) => {
    return await request(app.getHttpServer()).post('/api/users').send(userData);
};

export const getAuthToken = async (user) => {
    const response = await createUser(user);
    return response.body.token;
};

export const cleanDatabase = async () => {
    const collections = await mongoose.connection.db.collections();
    for (const collection of collections) {
        await collection.deleteMany({});
    }
};
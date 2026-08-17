import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../../src/app.module';
import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';

let mongod: MongoMemoryServer;

beforeAll(async () => {
    mongod = await MongoMemoryServer.create();
    const uri = mongod.getUri();
    await mongoose.connect(uri);
});

afterAll(async () => {
    await mongoose.disconnect();
    await mongod.stop();
});

describe('Auth Signup (e2e)', () => {
    let app: INestApplication;

    beforeAll(async () => {
        const moduleFixture: TestingModule = await Test.createTestingModule({
            imports: [AppModule],
        }).compile();

        app = moduleFixture.createNestApplication();
        await app.init();
    });

    afterAll(async () => {
        await app.close();
    });

    it('should register a new user successfully', async () => {
        const response = await request(app.getHttpServer())
            .post('/api/auth/signup')
            .send({
                first_name: 'John',
                last_name: 'Doe',
                email: 'john.doe@example.com',
                password: 'StrongPassword123!',
                terms_accepted: true
            });
        expect(response.status).toBe(201);
        expect(response.body).toHaveProperty('success', true);
        expect(response.body.data).toHaveProperty('email', 'john.doe@example.com');
    });

    it('should fail registration with missing fields', async () => {
        const response = await request(app.getHttpServer())
            .post('/api/auth/signup')
            .send({
                first_name: 'John',
                email: 'john.doe@example.com',
                password: 'StrongPassword123!'
            });
        expect(response.status).toBe(400);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'VALIDATION_ERROR');
    });

    it('should fail registration with duplicate email', async () => {
        await request(app.getHttpServer())
            .post('/api/auth/signup')
            .send({
                first_name: 'John',
                last_name: 'Doe',
                email: 'john.doe@example.com',
                password: 'StrongPassword123!',
                terms_accepted: true
            });

        const response = await request(app.getHttpServer())
            .post('/api/auth/signup')
            .send({
                first_name: 'Jane',
                last_name: 'Doe',
                email: 'john.doe@example.com',
                password: 'AnotherStrongPassword123!',
                terms_accepted: true
            });
        expect(response.status).toBe(409);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'DUPLICATE_EMAIL');
    });

    it('should fail registration with weak password', async () => {
        const response = await request(app.getHttpServer())
            .post('/api/auth/signup')
            .send({
                first_name: 'John',
                last_name: 'Doe',
                email: 'john.doe@example.com',
                password: 'weak',
                terms_accepted: true
            });
        expect(response.status).toBe(400);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'VALIDATION_ERROR');
    });

    it('should fail registration if terms are not accepted', async () => {
        const response = await request(app.getHttpServer())
            .post('/api/auth/signup')
            .send({
                first_name: 'John',
                last_name: 'Doe',
                email: 'john.doe@example.com',
                password: 'StrongPassword123!',
                terms_accepted: false
            });
        expect(response.status).toBe(400);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'TERMS_NOT_ACCEPTED');
    });
});
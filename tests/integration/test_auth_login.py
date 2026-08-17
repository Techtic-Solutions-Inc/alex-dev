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

describe('Auth Login (e2e)', () => {
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

    it('should login successfully with valid credentials', async () => {
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
            .post('/api/auth/login')
            .send({
                email: 'john.doe@example.com',
                password: 'StrongPassword123!'
            });
        expect(response.status).toBe(201);
        expect(response.body).toHaveProperty('success', true);
        expect(response.body.data).toHaveProperty('token');
    });

    it('should fail login with invalid email format', async () => {
        const response = await request(app.getHttpServer())
            .post('/api/auth/login')
            .send({
                email: 'invalid-email',
                password: 'StrongPassword123!'
            });
        expect(response.status).toBe(400);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'VALIDATION_ERROR');
    });

    it('should fail login for inactive user', async () => {
        await request(app.getHttpServer())
            .post('/api/auth/signup')
            .send({
                first_name: 'Inactive',
                last_name: 'User',
                email: 'inactive.user@example.com',
                password: 'StrongPassword123!',
                terms_accepted: true
            });

        // Simulate user deactivation
        await mongoose.connection.collection('users').updateOne(
            { email: 'inactive.user@example.com' },
            { $set: { is_active: false } }
        );

        const response = await request(app.getHttpServer())
            .post('/api/auth/login')
            .send({
                email: 'inactive.user@example.com',
                password: 'StrongPassword123!'
            });
        expect(response.status).toBe(403);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'USER_INACTIVE');
    });

    it('should fail login with incorrect password', async () => {
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
            .post('/api/auth/login')
            .send({
                email: 'john.doe@example.com',
                password: 'WrongPassword123!'
            });
        expect(response.status).toBe(401);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'INVALID_CREDENTIALS');
    });

    it('should fail login with weak password', async () => {
        const response = await request(app.getHttpServer())
            .post('/api/auth/login')
            .send({
                email: 'john.doe@example.com',
                password: 'weak'
            });
        expect(response.status).toBe(400);
        expect(response.body).toHaveProperty('success', false);
        expect(response.body.error).toHaveProperty('code', 'VALIDATION_ERROR');
    });
});
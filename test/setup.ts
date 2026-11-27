import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';
import { Test } from '@nestjs/testing';
import { AppModule } from '../src/app.module';
import request from 'supertest';

let mongoServer: MongoMemoryServer;
let app;

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
});

export const createUser = async (email, password, isActive = true) => {
  // Logic to create a user in the test database
};

export const loginUser = async (email, password) => {
  const response = await request(app).post('/api/auth/login').send({ email, password });
  return response.body.token;
};

export { app };

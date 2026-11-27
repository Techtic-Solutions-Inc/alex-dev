import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { JwtService } from '@nestjs/jwt';
import { ConfigService } from '@nestjs/config';

let app: INestApplication;
let jwtService: JwtService;

const users = [
  { email: 'admin@test.com', role: 'admin', password: 'TestAdmin123!', is_active: true },
  { email: 'user@test.com', role: 'user', password: 'TestUser123!', is_active: true },
  { email: 'viewer@test.com', role: 'viewer', password: 'TestViewer123!', is_active: true },
  { email: 'inactive@test.com', role: 'user', password: 'TestInactive123!', is_active: false },
  { email: 'newuser@test.com', role: 'user', password: 'NewUser123!', is_active: false },
];

async function setup() {
  const moduleFixture: TestingModule = await Test.createTestingModule({
    imports: [AppModule],
  }).compile();

  app = moduleFixture.createNestApplication();
  await app.init();

  jwtService = app.get<JwtService>(JwtService);
  const configService = app.get<ConfigService>(ConfigService);

  // Create users in the database
  for (const user of users) {
    await request(app.getHttpServer()).post('/api/signup').send({
      first_name: 'Test',
      last_name: 'User',
      email: user.email,
      password: user.password,
      terms_accepted: true,
    });
  }
}

async function teardown() {
  // Cleanup logic to remove users from the database
}

export { setup, teardown, app, jwtService };

import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { JwtService } from '@nestjs/jwt';

describe('Visitor Signup API (e2e)', () => {
  let app: INestApplication;
  let jwtService: JwtService;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    jwtService = app.get<JwtService>(JwtService);
  });

  afterAll(async () => {
    await app.close();
  });

  it('POST /api/signup should return 201 for successful signup', async () => {
    const response = await request(app.getHttpServer())
      .post('/api/signup')
      .send({
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'StrongPassword123!',
        terms_accepted: true,
      })
      .expect(201);
    expect(response.body.email).toEqual('john.doe@example.com');
  });

  it('POST /api/signup with empty first name should return 400', async () => {
    await request(app.getHttpServer())
      .post('/api/signup')
      .send({
        first_name: '',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'StrongPassword123!',
        terms_accepted: true,
      })
      .expect(400);
  });

  it('POST /api/signup with invalid email should return 400', async () => {
    await request(app.getHttpServer())
      .post('/api/signup')
      .send({
        first_name: 'John',
        last_name: 'Doe',
        email: 'invalid-email',
        password: 'StrongPassword123!',
        terms_accepted: true,
      })
      .expect(400);
  });

  it('POST /api/signup with duplicate email should return 409', async () => {
    await request(app.getHttpServer())
      .post('/api/signup')
      .send({
        first_name: 'John',
        last_name: 'Doe',
        email: 'john.doe@example.com',
        password: 'StrongPassword123!',
        terms_accepted: true,
      })
      .expect(409);
  });

  it('POST /api/signup without terms accepted should return 400', async () => {
    await request(app.getHttpServer())
      .post('/api/signup')
      .send({ first_name: 'John', last_name: 'Doe', email: 'john.doe@example.com', password: 'StrongPassword123!' })
      .expect(400);
  });
});

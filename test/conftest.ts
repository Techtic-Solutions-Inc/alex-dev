import { Test, TestingModule } from '@nestjs/testing';
import { MongooseModule } from '@nestjs/mongoose';
import { ContentLibraryModule } from '../src/modules/content-library/content-library.module';
import { ContentLibraryItem } from '../src/modules/content-library/entities/content-library-item.schema';
import { mockedContentLibraryItems } from './mockedContentLibraryItems';

const TEST_DATABASE_URL = process.env.TEST_DATABASE_URL || 'mongodb://localhost:27017/test_db';

export const setupTestModule = async () => {
  const moduleFixture: TestingModule = await Test.createTestingModule({
    imports: [MongooseModule.forRoot(TEST_DATABASE_URL), ContentLibraryModule],
  }).compile();

  return moduleFixture.createNestApplication();
};

export const createMockedContentLibraryItems = async (model) => {
  await model.insertMany(mockedContentLibraryItems);
};

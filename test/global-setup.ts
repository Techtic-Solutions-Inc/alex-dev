import { writeFileSync } from 'fs';
import { join } from 'path';
import { MongoMemoryServer } from 'mongodb-memory-server';

const mongoStatePath = join(__dirname, '.mongo-test-state.json');

export = async function globalSetup(): Promise<void> {
  const mongod = await MongoMemoryServer.create();
  const uri = mongod.getUri();
  process.env.DATABASE_URL = uri;
  process.env.MIGRATIONS_DATABASE_URL = uri;

  writeFileSync(
    mongoStatePath,
    JSON.stringify({
      uri,
    }),
    'utf8',
  );

  (global as { __MONGOD__?: MongoMemoryServer }).__MONGOD__ = mongod;
};

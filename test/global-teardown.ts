import { unlinkSync } from 'fs';
import { join } from 'path';
import { MongoMemoryServer } from 'mongodb-memory-server';

const mongoStatePath = join(__dirname, '.mongo-test-state.json');

export = async function globalTeardown(): Promise<void> {
  const mongod = (global as { __MONGOD__?: MongoMemoryServer }).__MONGOD__;
  if (mongod) {
    await mongod.stop();
  }

  try {
    unlinkSync(mongoStatePath);
  } catch {
    // State file may not exist if setup failed early.
  }
};

import mongoose from 'mongoose';
import { MongoMemoryServer } from 'mongodb-memory-server';

type MongoTestGlobal = typeof globalThis & {
  __E2E_MONGOD__?: MongoMemoryServer;
  __E2E_MONGOD_URI_PROMISE__?: Promise<string>;
};

const mongoGlobal = globalThis as MongoTestGlobal;

/**
 * Starts a single in-process MongoDB Memory Server for the e2e Jest worker.
 * Jest globalSetup runs in a separate process, so the server must live here.
 */
export function ensureMongoMemoryUri(): Promise<string> {
  if (!mongoGlobal.__E2E_MONGOD_URI_PROMISE__) {
    mongoGlobal.__E2E_MONGOD_URI_PROMISE__ = (async () => {
      if (mongoose.connection.readyState !== 0) {
        await mongoose.disconnect();
      }

      const mongod = await MongoMemoryServer.create();
      mongoGlobal.__E2E_MONGOD__ = mongod;
      const uri = mongod.getUri();
      process.env.DATABASE_URL = uri;
      process.env.MIGRATIONS_DATABASE_URL = uri;
      return uri;
    })();
  }
  return mongoGlobal.__E2E_MONGOD_URI_PROMISE__;
}

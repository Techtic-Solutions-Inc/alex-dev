import { mongo } from 'mongoose';
import { Migration } from './migration.interface';

type Db = mongo.Db;

const USERS_COLLECTION = 'users';
const SETTINGS_COLLECTION = 'app_settings';
const EMAIL_INDEX = 'uniq_users_email';
const VERIFICATION_TOKEN_INDEX = 'verification_token_hash_1';
const SCHEMA_VERSION_KEY = 'schema_version';

async function collectionExists(database: Db, name: string): Promise<boolean> {
  const collections = await database.listCollections({ name }, { nameOnly: true }).toArray();
  return collections.length > 0;
}

/**
 * Establishes the collections and indexes used by the initial API schema.
 * All operations are idempotent so a failed deployment can safely be retried.
 */
export const initialSchemaMigration: Migration = {
  id: '001-initial-schema',
  description: 'Create the users and application settings collections',
  checksum: 'sha256:12a1b2358f43471bc5a5aa2c9019b30c9b04c08cdd70b7ecfa3b75b7812c268e',

  async up(database: Db): Promise<void> {
    if (!(await collectionExists(database, USERS_COLLECTION))) {
      await database.createCollection(USERS_COLLECTION);
    }

    await database.collection(USERS_COLLECTION).createIndex(
      { email: 1 },
      {
        name: EMAIL_INDEX,
        unique: true,
        collation: { locale: 'en', strength: 2 },
      },
    );
    await database.collection(USERS_COLLECTION).createIndex(
      { verification_token_hash: 1 },
      {
        name: VERIFICATION_TOKEN_INDEX,
        sparse: true,
      },
    );

    if (!(await collectionExists(database, SETTINGS_COLLECTION))) {
      await database.createCollection(SETTINGS_COLLECTION);
    }

    await database.collection(SETTINGS_COLLECTION).updateOne(
      { key: SCHEMA_VERSION_KEY },
      {
        $setOnInsert: {
          key: SCHEMA_VERSION_KEY,
          value: 1,
          createdAt: new Date(),
        },
      },
      { upsert: true },
    );
  },

  async down(database: Db): Promise<void> {
    if (await collectionExists(database, SETTINGS_COLLECTION)) {
      await database.collection(SETTINGS_COLLECTION).deleteOne({ key: SCHEMA_VERSION_KEY });
    }

    if (await collectionExists(database, USERS_COLLECTION)) {
      for (const indexName of [VERIFICATION_TOKEN_INDEX, EMAIL_INDEX]) {
        try {
          await database.collection(USERS_COLLECTION).dropIndex(indexName);
        } catch (error) {
          if (!(error instanceof mongo.MongoServerError) || error.code !== 27) {
            throw error;
          }
        }
      }
    }
  },
};

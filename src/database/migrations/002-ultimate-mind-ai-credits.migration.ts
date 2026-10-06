import { mongo } from 'mongoose';
import { Migration } from './migration.interface';

type Db = mongo.Db;

const COLLECTION = 'ultimate_mind_ai_credit_records';
const UNIQUE_INDEX = 'uniq_active_ultimate_mind_ai_credit_per_user';

async function collectionExists(database: Db, name: string): Promise<boolean> {
  const collections = await database.listCollections({ name }, { nameOnly: true }).toArray();
  return collections.length > 0;
}

/**
 * Creates the Ultimate Mind AI credit records collection and supporting indexes.
 * All operations are idempotent so a failed deployment can safely be retried.
 */
export const ultimateMindAiCreditsMigration: Migration = {
  id: '002-ultimate-mind-ai-credits',
  description: 'Create the ultimate_mind_ai_credit_records collection and indexes',
  checksum: 'sha256:8f3c1a9b2d4e6f708192a3b5c7d9e0f1a2b3c4d5e6f708192a3b5c7d9e0f1a2',

  async up(database: Db): Promise<void> {
    if (!(await collectionExists(database, COLLECTION))) {
      await database.createCollection(COLLECTION);
    }

    await database.collection(COLLECTION).createIndex(
      { user_id: 1, is_active: 1 },
      {
        name: UNIQUE_INDEX,
        unique: true,
        partialFilterExpression: { is_active: true },
      },
    );
  },

  async down(database: Db): Promise<void> {
    if (!(await collectionExists(database, COLLECTION))) {
      return;
    }

    try {
      await database.collection(COLLECTION).dropIndex(UNIQUE_INDEX);
    } catch (error) {
      if (!(error instanceof mongo.MongoServerError) || error.code !== 27) {
        throw error;
      }
    }
  },
};

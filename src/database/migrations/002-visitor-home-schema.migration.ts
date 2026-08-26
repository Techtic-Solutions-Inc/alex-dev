import { mongo } from 'mongoose';
import { Migration } from './migration.interface';

type Db = mongo.Db;

const CONTENTS_COLLECTION = 'visitor_home_contents';
const SUBSCRIPTIONS_COLLECTION = 'visitor_home_subscriptions';
const SUBSCRIPTION_EMAIL_INDEX = 'uniq_visitor_home_subscriptions_email';

async function collectionExists(database: Db, name: string): Promise<boolean> {
  const collections = await database.listCollections({ name }, { nameOnly: true }).toArray();
  return collections.length > 0;
}

/**
 * Creates the public visitor Home content and marketing-subscription collections.
 * All operations are idempotent so a failed deployment can safely be retried.
 */
export const visitorHomeSchemaMigration: Migration = {
  id: '002-visitor-home-schema',
  description: 'Create visitor home content and subscription collections',
  checksum: 'sha256:7c3e9a1f4b82d6e05a91c8f0d3b47e6a2c15f9d84e0b1a6c3d7f2e8a9b4c5d01',

  async up(database: Db): Promise<void> {
    if (!(await collectionExists(database, CONTENTS_COLLECTION))) {
      await database.createCollection(CONTENTS_COLLECTION);
    }

    if (!(await collectionExists(database, SUBSCRIPTIONS_COLLECTION))) {
      await database.createCollection(SUBSCRIPTIONS_COLLECTION);
    }

    await database.collection(SUBSCRIPTIONS_COLLECTION).createIndex(
      { email: 1 },
      {
        name: SUBSCRIPTION_EMAIL_INDEX,
        unique: true,
        collation: { locale: 'en', strength: 2 },
      },
    );
  },

  async down(database: Db): Promise<void> {
    if (!(await collectionExists(database, SUBSCRIPTIONS_COLLECTION))) {
      return;
    }

    try {
      await database.collection(SUBSCRIPTIONS_COLLECTION).dropIndex(SUBSCRIPTION_EMAIL_INDEX);
    } catch (error) {
      if (!(error instanceof mongo.MongoServerError) || error.code !== 27) {
        throw error;
      }
    }
  },
};

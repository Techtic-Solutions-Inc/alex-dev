import { ensureCollection, dropIndexIfExists } from './migration-helpers';
import { Migration } from './migration.interface';

const COLLECTION = 'real_estate_professional_contents';
const UNIQUE_TITLE = 'uniq_active_rep_content_title_per_user';
const TEXT_INDEX = 'title_text_description_text_tags_text_city_text';

export const realEstateProfessionalContentMigration: Migration = {
  id: '003-real-estate-professional-content',
  description: 'Create Real Estate Professional content collection and indexes',
  checksum: 'sha256:f4c2d9a81e7053c4b91ad62e0f58c4d7e6a1b903c5f8e2d41a7c6b9053e1d4f2',

  async up(database): Promise<void> {
    await ensureCollection(database, COLLECTION);
    const collection = database.collection(COLLECTION);
    await collection.createIndex({ user_id: 1 });
    await collection.createIndex(
      { user_id: 1, title: 1, is_active: 1 },
      {
        name: UNIQUE_TITLE,
        unique: true,
        partialFilterExpression: { is_active: true },
        collation: { locale: 'en', strength: 2 },
      },
    );
    await collection.createIndex(
      { title: 'text', description: 'text', tags: 'text', city: 'text' },
      { name: TEXT_INDEX },
    );
  },

  async down(database): Promise<void> {
    for (const indexName of [TEXT_INDEX, UNIQUE_TITLE, 'user_id_1']) {
      await dropIndexIfExists(database, COLLECTION, indexName);
    }
  },
};
import { mongo } from 'mongoose';
import { dropIndexIfExists, ensureCollection } from './migration-helpers';
import { Migration } from './migration.interface';

type Db = mongo.Db;

const CONTENT_LIBRARY = 'content_library_items';
const CONTENT_CALENDAR = 'content_calendar_entries';
const DASHBOARD_ANNOUNCEMENTS = 'dashboard_announcements';
const PROFILE_CONTENTS = 'profile_contents';
const PROFILE_DOWNLOADS = 'profile_downloads';

const INDEXES = {
  contentLibrary: {
    userId: 'user_id_1',
    category: 'category_1',
    isActive: 'is_active_1',
    uniqueTitle: 'uniq_active_content_library_title_category_per_user',
    textSearch: 'title_text_description_text_category_text_tags_text',
  },
  contentCalendar: {
    userId: 'user_id_1',
    isActive: 'is_active_1',
    uniqueTitleDate: 'uniq_active_calendar_title_date_per_user',
  },
  dashboardAnnouncements: {
    userId: 'user_id_1',
    uniqueTitle: 'uniq_dashboard_announcement_title_per_user',
  },
  profileContents: {
    userId: 'user_id_1',
    list: 'idx_profile_contents_user_active_updated',
  },
  profileDownloads: {
    userId: 'user_id_1',
    list: 'idx_profile_downloads_user_active_last_downloaded',
  },
} as const;

/**
 * Creates the domain collections and indexes used by content, calendar,
 * dashboard, and profile modules. Operations are idempotent for safe retries.
 */
export const domainCollectionsMigration: Migration = {
  id: '002-domain-collections',
  description: 'Create domain collections and compound indexes for application modules',
  checksum: 'sha256:9c3f8e21a4b7d602e5f1c8340a6d92b7e4f0a18c5d39e72b1f4a8063c9d5e71',

  async up(database: Db): Promise<void> {
    await ensureCollection(database, CONTENT_LIBRARY);
    const contentLibrary = database.collection(CONTENT_LIBRARY);
    await contentLibrary.createIndex({ user_id: 1 }, { name: INDEXES.contentLibrary.userId });
    await contentLibrary.createIndex({ category: 1 }, { name: INDEXES.contentLibrary.category });
    await contentLibrary.createIndex({ is_active: 1 }, { name: INDEXES.contentLibrary.isActive });
    await contentLibrary.createIndex(
      { user_id: 1, title: 1, category: 1, is_active: 1 },
      {
        name: INDEXES.contentLibrary.uniqueTitle,
        unique: true,
        partialFilterExpression: { is_active: true },
        collation: { locale: 'en', strength: 2 },
      },
    );
    await contentLibrary.createIndex(
      { title: 'text', description: 'text', category: 'text', tags: 'text' },
      { name: INDEXES.contentLibrary.textSearch },
    );

    await ensureCollection(database, CONTENT_CALENDAR);
    const contentCalendar = database.collection(CONTENT_CALENDAR);
    await contentCalendar.createIndex({ user_id: 1 }, { name: INDEXES.contentCalendar.userId });
    await contentCalendar.createIndex({ is_active: 1 }, { name: INDEXES.contentCalendar.isActive });
    await contentCalendar.createIndex(
      { user_id: 1, title: 1, date: 1, is_active: 1 },
      {
        name: INDEXES.contentCalendar.uniqueTitleDate,
        unique: true,
        partialFilterExpression: { is_active: true },
        collation: { locale: 'en', strength: 2 },
      },
    );

    await ensureCollection(database, DASHBOARD_ANNOUNCEMENTS);
    const announcements = database.collection(DASHBOARD_ANNOUNCEMENTS);
    await announcements.createIndex({ user_id: 1 }, { name: INDEXES.dashboardAnnouncements.userId });
    await announcements.createIndex(
      { user_id: 1, announcement_title: 1 },
      {
        name: INDEXES.dashboardAnnouncements.uniqueTitle,
        unique: true,
        collation: { locale: 'en', strength: 2 },
      },
    );

    await ensureCollection(database, PROFILE_CONTENTS);
    const profileContents = database.collection(PROFILE_CONTENTS);
    await profileContents.createIndex({ user_id: 1 }, { name: INDEXES.profileContents.userId });
    await profileContents.createIndex(
      { user_id: 1, is_active: 1, updatedAt: -1 },
      { name: INDEXES.profileContents.list },
    );

    await ensureCollection(database, PROFILE_DOWNLOADS);
    const profileDownloads = database.collection(PROFILE_DOWNLOADS);
    await profileDownloads.createIndex({ user_id: 1 }, { name: INDEXES.profileDownloads.userId });
    await profileDownloads.createIndex(
      { user_id: 1, is_active: 1, last_downloaded_at: -1 },
      { name: INDEXES.profileDownloads.list },
    );
  },

  async down(database: Db): Promise<void> {
    for (const indexName of Object.values(INDEXES.profileDownloads)) {
      await dropIndexIfExists(database, PROFILE_DOWNLOADS, indexName);
    }
    for (const indexName of Object.values(INDEXES.profileContents)) {
      await dropIndexIfExists(database, PROFILE_CONTENTS, indexName);
    }
    for (const indexName of Object.values(INDEXES.dashboardAnnouncements)) {
      await dropIndexIfExists(database, DASHBOARD_ANNOUNCEMENTS, indexName);
    }
    for (const indexName of Object.values(INDEXES.contentCalendar)) {
      await dropIndexIfExists(database, CONTENT_CALENDAR, indexName);
    }
    for (const indexName of Object.values(INDEXES.contentLibrary)) {
      await dropIndexIfExists(database, CONTENT_LIBRARY, indexName);
    }
  },
};
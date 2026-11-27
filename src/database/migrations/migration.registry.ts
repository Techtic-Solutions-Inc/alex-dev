import { initialSchemaMigration } from './001-initial-schema.migration';
import { domainCollectionsMigration } from './002-domain-collections.migration';
import { realEstateProfessionalContentMigration } from './003-real-estate-professional-content.migration';
import { Migration } from './migration.interface';

/**
 * Ordered list of all migrations known to this deployment. Add new migrations
 * here in lexically increasing ID order; never reorder or remove entries that
 * may already be recorded in `_schema_migrations`.
 */
export const migrationRegistry: readonly Migration[] = [
  initialSchemaMigration,
  domainCollectionsMigration,
  realEstateProfessionalContentMigration,
];
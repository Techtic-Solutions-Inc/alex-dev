import { mongo } from 'mongoose';

type Db = mongo.Db;

/**
 * A versioned, reversible database change.
 *
 * Migration IDs must be lexically sortable and immutable once deployed.
 * Implementations must make both operations safe to retry because MongoDB
 * deployments without transactions can be interrupted between operations.
 */
export interface Migration {
  readonly id: string;
  readonly description: string;
  /**
   * Update when the behavior of a migration changes. Never edit a migration
   * that has already been applied in an environment; create a new migration.
   */
  readonly checksum: string;
  up(database: Db): Promise<void>;
  down(database: Db): Promise<void>;
}

export interface AppliedMigration {
  readonly _id: string;
  readonly checksum: string;
  readonly description: string;
  readonly appliedAt: Date;
}

export type MigrationStatus = 'applied' | 'pending';

export interface MigrationStatusEntry {
  readonly id: string;
  readonly description: string;
  readonly status: MigrationStatus;
  readonly appliedAt: Date | null;
}

export interface MigrationRunResult {
  readonly applied: readonly string[];
  readonly skipped: readonly string[];
}

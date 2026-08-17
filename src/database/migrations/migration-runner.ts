import { mongo } from 'mongoose';
import { AppliedMigration, Migration, MigrationRunResult, MigrationStatusEntry } from './migration.interface';

type Db = mongo.Db;

const DEFAULT_LEDGER_COLLECTION = '_schema_migrations';
const DEFAULT_LOCK_COLLECTION = '_schema_migration_locks';
const LOCK_ID = 'migration-runner';

export class MigrationError extends Error {
  constructor(
    message: string,
    public readonly code:
      'MIGRATION_LOCKED' | 'MIGRATION_CHECKSUM_MISMATCH' | 'INVALID_MIGRATION_REGISTRY' | 'INVALID_ROLLBACK_COUNT',
  ) {
    super(message);
    this.name = 'MigrationError';
  }
}

export interface MigrationRunnerOptions {
  readonly ledgerCollection?: string;
  readonly lockCollection?: string;
  readonly owner?: string;
}

/**
 * Applies and reverts ordered migrations while persisting their state in
 * MongoDB. This runner is intentionally independent of the Nest application
 * lifecycle so deployments can migrate before starting API instances.
 */
export class MigrationRunner {
  private readonly ledgerCollection: string;
  private readonly lockCollection: string;
  private readonly owner: string;

  constructor(
    private readonly database: Db,
    private readonly migrations: readonly Migration[],
    options: MigrationRunnerOptions = {},
  ) {
    this.ledgerCollection = options.ledgerCollection ?? DEFAULT_LEDGER_COLLECTION;
    this.lockCollection = options.lockCollection ?? DEFAULT_LOCK_COLLECTION;
    this.owner = options.owner ?? `${process.env.HOSTNAME ?? 'unknown'}:${process.pid}`;
    this.validateMigrations();
  }

  async status(): Promise<MigrationStatusEntry[]> {
    const applied = await this.appliedById();
    return this.migrations.map((migration) => {
      const record = applied.get(migration.id);
      if (record && record.checksum !== migration.checksum) {
        throw new MigrationError(
          `Migration "${migration.id}" does not match the version recorded in the database.`,
          'MIGRATION_CHECKSUM_MISMATCH',
        );
      }

      return {
        id: migration.id,
        description: migration.description,
        status: record ? 'applied' : 'pending',
        appliedAt: record?.appliedAt ?? null,
      };
    });
  }

  async up(): Promise<MigrationRunResult> {
    return this.withLock(async () => {
      const applied = await this.appliedById();
      const result: { applied: string[]; skipped: string[] } = { applied: [], skipped: [] };

      for (const migration of this.migrations) {
        const record = applied.get(migration.id);
        if (record) {
          this.assertChecksum(migration, record);
          result.skipped.push(migration.id);
          continue;
        }

        await migration.up(this.database);
        await this.database.collection<AppliedMigration>(this.ledgerCollection).insertOne({
          _id: migration.id,
          checksum: migration.checksum,
          description: migration.description,
          appliedAt: new Date(),
        });
        result.applied.push(migration.id);
      }

      return result;
    });
  }

  async down(count = 1): Promise<string[]> {
    if (!Number.isSafeInteger(count) || count < 1) {
      throw new MigrationError('Rollback count must be a positive integer.', 'INVALID_ROLLBACK_COUNT');
    }

    return this.withLock(async () => {
      const applied = await this.appliedById();
      const rollbackCandidates = [...this.migrations]
        .reverse()
        .filter((migration) => applied.has(migration.id))
        .slice(0, count);

      for (const migration of rollbackCandidates) {
        const record = applied.get(migration.id);
        if (!record) {
          continue;
        }

        this.assertChecksum(migration, record);
        await migration.down(this.database);
        await this.database.collection<AppliedMigration>(this.ledgerCollection).deleteOne({
          _id: migration.id,
        });
      }

      return rollbackCandidates.map((migration) => migration.id);
    });
  }

  private async appliedById(): Promise<Map<string, AppliedMigration>> {
    const records = await this.database.collection<AppliedMigration>(this.ledgerCollection).find({}).toArray();
    return new Map(records.map((record) => [record._id, record]));
  }

  private assertChecksum(migration: Migration, record: AppliedMigration): void {
    if (migration.checksum !== record.checksum) {
      throw new MigrationError(
        `Migration "${migration.id}" does not match the version recorded in the database.`,
        'MIGRATION_CHECKSUM_MISMATCH',
      );
    }
  }

  private async withLock<T>(operation: () => Promise<T>): Promise<T> {
    const locks = this.database.collection<{ _id: string; owner: string; acquiredAt: Date }>(this.lockCollection);

    try {
      await locks.insertOne({ _id: LOCK_ID, owner: this.owner, acquiredAt: new Date() });
    } catch (error) {
      if (this.isDuplicateKeyError(error)) {
        throw new MigrationError(
          'Another migration process is already running. Wait for it to finish before retrying.',
          'MIGRATION_LOCKED',
        );
      }
      throw error;
    }

    try {
      return await operation();
    } finally {
      await locks.deleteOne({ _id: LOCK_ID, owner: this.owner });
    }
  }

  private validateMigrations(): void {
    const ids = this.migrations.map((migration) => migration.id);
    const hasDuplicate = new Set(ids).size !== ids.length;
    const isUnordered = ids.some((id, index) => index > 0 && ids[index - 1] >= id);
    const hasInvalidMigration = this.migrations.some(
      (migration) =>
        !migration.id ||
        !migration.description ||
        !migration.checksum ||
        typeof migration.up !== 'function' ||
        typeof migration.down !== 'function',
    );

    if (hasDuplicate || isUnordered || hasInvalidMigration) {
      throw new MigrationError(
        'Migrations must have unique, increasing IDs and implement up/down operations.',
        'INVALID_MIGRATION_REGISTRY',
      );
    }
  }

  private isDuplicateKeyError(error: unknown): boolean {
    return error instanceof mongo.MongoServerError && error.code === 11000;
  }
}

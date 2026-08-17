import mongoose from 'mongoose';
import { initialSchemaMigration } from './001-initial-schema.migration';
import { MigrationError, MigrationRunner } from './migration-runner';

type MigrationCommand = 'up' | 'down' | 'status';

function parseCommand(argumentsList: readonly string[]): { command: MigrationCommand; count?: number } {
  const [command, countValue] = argumentsList;
  if (command !== 'up' && command !== 'down' && command !== 'status') {
    throw new Error('Usage: migration <up|down|status> [rollback-count]');
  }

  if (command !== 'down') {
    if (countValue) {
      throw new Error('Only the down command accepts a rollback count.');
    }
    return { command };
  }

  if (!countValue) {
    return { command, count: 1 };
  }

  if (!/^[1-9]\d*$/.test(countValue)) {
    throw new Error('Rollback count must be a positive integer.');
  }

  return { command, count: Number(countValue) };
}

async function main(): Promise<void> {
  const { command, count } = parseCommand(process.argv.slice(2));
  const uri = process.env.MIGRATIONS_DATABASE_URL ?? process.env.DATABASE_URL;
  if (!uri) {
    throw new Error('Set MIGRATIONS_DATABASE_URL or DATABASE_URL before running migrations.');
  }

  const connection = await mongoose.createConnection(uri, { serverSelectionTimeoutMS: 10_000 }).asPromise();

  try {
    if (!connection.db) {
      throw new Error('Unable to establish a database connection for migrations.');
    }

    const runner = new MigrationRunner(connection.db, [initialSchemaMigration], {
      owner: process.env.MIGRATION_RUNNER_ID,
    });

    if (command === 'status') {
      const status = await runner.status();
      for (const migration of status) {
        const timestamp = migration.appliedAt?.toISOString() ?? '-';
        console.log(`${migration.id}\t${migration.status}\t${timestamp}\t${migration.description}`);
      }
      return;
    }

    if (command === 'up') {
      const result = await runner.up();
      console.log(`Applied ${result.applied.length} migration(s).`);
      return;
    }

    const reverted = await runner.down(count);
    console.log(`Reverted ${reverted.length} migration(s).`);
  } finally {
    await connection.close();
  }
}

void main().catch((error: unknown) => {
  const message =
    error instanceof MigrationError || error instanceof Error
      ? error.message
      : 'Migration command failed unexpectedly.';
  console.error(`Migration failed: ${message}`);
  process.exitCode = 1;
});

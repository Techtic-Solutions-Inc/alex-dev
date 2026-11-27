import mongoose from 'mongoose';
import { migrationRegistry } from '../src/database/migrations/migration.registry';
import { MigrationRunner } from '../src/database/migrations/migration-runner';
import { ensureMongoMemoryUri } from './mongodb-memory';

describe('Database migrations (e2e)', () => {
  beforeAll(async () => {
    await ensureMongoMemoryUri();
  });

  afterAll(async () => {
    // Leave the shared in-process memory server running for other e2e files in this worker.
  });

  it('applies and rolls back registry migrations against in-memory MongoDB', async () => {
    const connection = mongoose.createConnection(process.env.DATABASE_URL!);
    await connection.asPromise();

    const database = connection.db;
    if (!database) {
      throw new Error('Expected MongoDB database handle after in-memory connection');
    }

    const runner = new MigrationRunner(database, migrationRegistry, { owner: 'e2e-migrations' });
    const upResult = await runner.up();

    expect(upResult.applied.length).toBeGreaterThan(0);
    const statusAfterUp = await runner.status();
    expect(statusAfterUp.every((entry) => entry.status === 'applied')).toBe(true);

    const reverted = await runner.down(1);
    expect(reverted).toHaveLength(1);

    await connection.close();
  });
});

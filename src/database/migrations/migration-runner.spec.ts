import { mongo } from 'mongoose';
import { initialSchemaMigration } from './001-initial-schema.migration';
import { Migration } from './migration.interface';
import { MigrationError, MigrationRunner } from './migration-runner';

type StoredDocument = Record<string, unknown> & { _id?: string; key?: string };

class FakeCollection {
  readonly documents = new Map<string, StoredDocument>();
  readonly indexes = new Set<string>();

  async insertOne(document: StoredDocument): Promise<void> {
    const identifier = document._id;
    if (!identifier || this.documents.has(identifier)) {
      throw new Error('duplicate key');
    }
    this.documents.set(identifier, document);
  }

  async deleteOne(filter: StoredDocument): Promise<void> {
    const record = Array.from(this.documents.entries()).find(([, document]) =>
      Object.entries(filter).every(([key, value]) => document[key] === value),
    );
    if (record) {
      this.documents.delete(record[0]);
    }
  }

  find(): { toArray: () => Promise<StoredDocument[]> } {
    return { toArray: async () => Array.from(this.documents.values()) };
  }

  async createIndex(_keys: StoredDocument, options: { name?: string } = {}): Promise<string> {
    const name = options.name ?? 'unnamed';
    this.indexes.add(name);
    return name;
  }

  async dropIndex(name: string): Promise<void> {
    this.indexes.delete(name);
  }

  async updateOne(
    filter: StoredDocument,
    update: { $setOnInsert?: StoredDocument },
    options: { upsert?: boolean },
  ): Promise<void> {
    const existing = Array.from(this.documents.values()).some((document) =>
      Object.entries(filter).every(([key, value]) => document[key] === value),
    );
    if (!existing && options.upsert && update.$setOnInsert) {
      const document = update.$setOnInsert;
      this.documents.set(String(document.key), document);
    }
  }
}

class FakeDatabase {
  private readonly collections = new Map<string, FakeCollection>();
  private readonly existingCollections = new Set<string>();

  collection(name: string): FakeCollection {
    let collection = this.collections.get(name);
    if (!collection) {
      collection = new FakeCollection();
      this.collections.set(name, collection);
    }
    return collection;
  }

  listCollections(filter: { name: string }): { toArray: () => Promise<{ name: string }[]> } {
    return {
      toArray: async () => (this.existingCollections.has(filter.name) ? [{ name: filter.name }] : []),
    };
  }

  async createCollection(name: string): Promise<void> {
    this.existingCollections.add(name);
    this.collection(name);
  }
}

const asDatabase = (database: FakeDatabase): mongo.Db => database as unknown as mongo.Db;

describe('MigrationRunner', () => {
  it('applies pending migrations once and records their version', async () => {
    const database = new FakeDatabase();
    const events: string[] = [];
    const migrations: Migration[] = [
      {
        id: '001-first',
        description: 'First migration',
        checksum: 'first',
        up: async () => {
          events.push('up:first');
        },
        down: async () => {
          events.push('down:first');
        },
      },
      {
        id: '002-second',
        description: 'Second migration',
        checksum: 'second',
        up: async () => {
          events.push('up:second');
        },
        down: async () => {
          events.push('down:second');
        },
      },
    ];
    const runner = new MigrationRunner(asDatabase(database), migrations);

    expect(await runner.up()).toEqual({
      applied: ['001-first', '002-second'],
      skipped: [],
    });
    expect(await runner.up()).toEqual({
      applied: [],
      skipped: ['001-first', '002-second'],
    });
    expect(events).toEqual(['up:first', 'up:second']);
  });

  it('reverts applied migrations in reverse order and removes ledger entries', async () => {
    const database = new FakeDatabase();
    const events: string[] = [];
    const migrations: Migration[] = [
      {
        id: '001-first',
        description: 'First migration',
        checksum: 'first',
        up: async () => {
          events.push('up:first');
        },
        down: async () => {
          events.push('down:first');
        },
      },
      {
        id: '002-second',
        description: 'Second migration',
        checksum: 'second',
        up: async () => {
          events.push('up:second');
        },
        down: async () => {
          events.push('down:second');
        },
      },
    ];
    const runner = new MigrationRunner(asDatabase(database), migrations);

    await runner.up();
    await expect(runner.down()).resolves.toEqual(['002-second']);
    expect(events).toEqual(['up:first', 'up:second', 'down:second']);
    await expect(runner.status()).resolves.toEqual([
      expect.objectContaining({ id: '001-first', status: 'applied' }),
      expect.objectContaining({ id: '002-second', status: 'pending' }),
    ]);
  });

  it('creates and rolls back the initial schema artifacts idempotently', async () => {
    const database = new FakeDatabase();
    const runner = new MigrationRunner(asDatabase(database), [initialSchemaMigration]);

    await runner.up();
    expect(database.collection('users').indexes).toContain('uniq_users_email');
    expect(database.collection('users').indexes).toContain('verification_token_hash_1');
    expect(database.collection('app_settings').documents.get('schema_version')).toEqual(
      expect.objectContaining({ value: 1 }),
    );

    await runner.down();
    expect(database.collection('users').indexes).not.toContain('uniq_users_email');
    expect(database.collection('users').indexes).not.toContain('verification_token_hash_1');
    expect(database.collection('app_settings').documents.get('schema_version')).toBeUndefined();
  });

  it('rejects a changed migration checksum', async () => {
    const database = new FakeDatabase();
    const original: Migration = {
      id: '001-first',
      description: 'First migration',
      checksum: 'original',
      up: async () => undefined,
      down: async () => undefined,
    };
    await new MigrationRunner(asDatabase(database), [original]).up();

    const changed: Migration = { ...original, checksum: 'changed' };
    await expect(new MigrationRunner(asDatabase(database), [changed]).status()).rejects.toEqual(
      expect.objectContaining<Partial<MigrationError>>({
        code: 'MIGRATION_CHECKSUM_MISMATCH',
      }),
    );
  });
});

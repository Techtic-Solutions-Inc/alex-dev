# Backend API

## Database migrations

MongoDB migrations are versioned TypeScript changes in
`src/database/migrations`. They are executed by a standalone runner rather
than when the Nest application starts. This allows a deployment to migrate the
database before API instances receive traffic.

The runner stores applied versions and immutable checksums in
`_schema_migrations`, and takes an exclusive lock in
`_schema_migration_locks`. A checksum mismatch stops execution: do not alter a
migration that has reached an environment. Create a new migration instead.

### Configuration

Copy `.env.example` and set `MIGRATIONS_DATABASE_URL` to the target MongoDB
database. If it is omitted, the runner uses `DATABASE_URL`. The migration
command reads environment variables supplied by the shell or deployment
platform; for local development, load your `.env` file before invoking it:

```bash
set -a && . ./.env && set +a
```

Use a separate database name for development and test environments. Never run
rollback commands against a production URI without an approved recovery plan.

### Commands

```bash
# Report every known migration and its state
npm run migration:status

# Apply all pending migrations in increasing ID order
npm run migration:up

# Revert the latest applied migration
npm run migration:down

# Revert the latest two migrations
npm run migration:down -- 2

# Compile once, then use the production runner
npm run build
npm run migration:up:prod
```

Migrations are protected against concurrent execution. If a deployment is
interrupted after acquiring the lock, verify that no migration process is
running, investigate the incomplete change, then remove the stale
`_schema_migration_locks` document before retrying. Migrations must therefore
make `up` and `down` safe to retry.

### Writing a migration

Create a lexically increasing file name and add its exported migration to the
registry in `migration.cli.ts`. Each migration requires an immutable `id`,
description, checksum, and both `up` and `down` functions. The initial
migration creates the `users` collection, a case-insensitive unique email
index, a sparse verification-token lookup index, and the `app_settings`
schema-version seed. Its rollback removes only those indexes and seed; it
intentionally never deletes application data.

Do not edit a deployed migration, perform unbounded collection scans, or
assume multi-document MongoDB transactions are available. Use idempotent
operations and deploy schema-compatible application code before applying
destructive migrations.

### Tests

The migration suite verifies application ordering, idempotent re-runs,
checksum protection, rollback ordering, and the initial migration's schema
artifacts without contacting a shared database:

```bash
npm run test:migrations
```
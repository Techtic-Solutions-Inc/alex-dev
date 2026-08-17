# Project setup

## API service

The backend is a FastAPI application located in `backend`. Copy
`backend/.env.example` to `backend/.env`, set a unique `JWT_SECRET`, then start
the service from `backend`:

```bash
uvicorn app.main:app --reload
```

Swagger UI is available at `/docs`. The liveness/readiness probe is available
at `GET /health` (and versioned at `GET /api/v1/health`). Authentication routes
are versioned under `/api/v1/auth`: `signup`, `login`, and refresh-token
rotation at `refresh`. Every endpoint returns a stable success/error envelope.

Run checks from `backend`:

```bash
python -m ruff check app tests ../tests
pytest -q
```

## MongoDB migrations

MongoDB schema and data changes are managed as ordered Python migrations in
`backend/app/db/migrations`. The runner records applied revisions in the
`_migrations` collection and uses a short-lived database lock, so only one
deployment can modify a database at a time.

Configure each environment with:

| Variable | Purpose |
| --- | --- |
| `APP_ENV` | Set to `development`, `staging`, `production`, or `test`; only `test` loads `.env.test` files. |
| `MONGODB_URL` | MongoDB connection URL for development, staging, or production. |
| `DB_NAME` | Database to migrate. |
| `MIGRATIONS_COLLECTION` | Optional migration ledger collection; defaults to `_migrations`. |
| `MIGRATIONS_LOCK_COLLECTION` | Optional lock collection; defaults to `_migration_locks`. |
| `MIGRATION_LOCK_TIMEOUT_SECONDS` | Lock expiry in seconds; defaults to `60`. |

Run commands from `backend` after making `app` importable:

```bash
python -m app.db.migrations status
python -m app.db.migrations upgrade
python -m app.db.migrations upgrade --target 0001_initial_schema
python -m app.db.migrations downgrade --target 0001_initial_schema
python -m app.db.migrations downgrade
```

`upgrade` is idempotent. `downgrade --target REVISION` keeps the named revision
and removes later revisions; omitting `--target` rolls back to the base schema.
The initial migration only drops empty collections during rollback. It refuses
to delete application documents, leaves the migration ledger intact, and exits
non-zero instead. Back up production data and verify the `status` output before
any rollback.

To add a migration, create a class implementing `Migration` with a unique,
immutable revision, explicit `upgrade` and `downgrade` methods, and register an
instance in `backend/app/db/migrations/__init__.py`. Never change an already
applied migration's revision or description because the runner detects its
checksum change.

### Testing migrations

Migration integration tests require an isolated MongoDB instance:

```bash
export TEST_MONGODB_URL='mongodb://localhost:27017'
export TEST_DB_NAME='test_project_migrations'
pytest tests/integration/test_migrations.py
```

The test database name must begin with `test`; the suite drops it before and
after each test. This verifies the initial upgrade, re-run idempotency, rollback
to base, reapplication, and rollback protection when collection data exists.
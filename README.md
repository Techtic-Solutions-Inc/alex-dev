# alex-dev

FastAPI backend with PostgreSQL and Alembic database migrations.

## Backend

See [backend/README.md](backend/README.md) for setup, API documentation, and development instructions.

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) to manage PostgreSQL schema changes. Migration scripts live in `backend/app/db/migrations/versions/` and are version-controlled in this repository.

All Alembic commands should be run from the `backend/` directory:

```bash
cd backend
```

### Apply migrations

```bash
alembic upgrade head
```

### Create a new migration

After changing SQLAlchemy models in `backend/app/models/`, autogenerate a revision:

```bash
alembic revision --autogenerate -m "Describe your change"
```

Review the generated script in `backend/app/db/migrations/versions/` before applying it.

### Roll back migrations

Roll back one revision:

```bash
alembic downgrade -1
```

Roll back to a specific revision:

```bash
alembic downgrade <revision_id>
```

Roll back all migrations:

```bash
alembic downgrade base
```

### Check current revision

```bash
alembic current
```

### Run migration tests

```bash
cd backend
pytest tests/integration/test_migrations.py
```

Set `TEST_DATABASE_URL` to point at a dedicated PostgreSQL database for integration tests (defaults to `postgresql+psycopg2://postgres:1234@localhost:5432/backend_migration_test`).

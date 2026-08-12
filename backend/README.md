# Backend API

Production-ready FastAPI backend with PostgreSQL, JWT authentication, structured logging, and Alembic migrations.

## Project Structure

```
backend/
  app/
    main.py                 # ASGI entry point
    api/v1/                 # API routers and endpoints
    core/                   # Config, security, logging
    db/                     # Session, base, migrations
    models/                 # SQLAlchemy ORM models
    schemas/                # Pydantic request/response schemas
    services/               # Business logic
    repositories/           # Data access layer
    middleware/             # Auth, logging, rate limiting
    dependencies/           # FastAPI dependency injection
    exceptions/             # Custom exceptions and handlers
  tests/
    unit/
    integration/
  scripts/
```

## Setup

1. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies (handled separately via dependency management).

3. Run migrations:
   ```bash
   alembic upgrade head
   ```

4. Start the server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Access API docs at `http://localhost:8000/docs`.

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database schema migrations.

### Create a new migration

After modifying SQLAlchemy models in `app/models/`, generate a migration:

```bash
alembic revision --autogenerate -m "Describe your change"
```

Review the generated script in `app/db/migrations/versions/` before applying.

### Apply migrations

```bash
alembic upgrade head
```

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

## Testing

```bash
pytest
```

Migration integration tests require a running PostgreSQL instance. Optionally set a dedicated test database:

```bash
export TEST_DATABASE_URL=postgresql+psycopg2://postgres:1234@localhost:5432/backend_migration_test
pytest tests/integration/test_migrations.py
```

## Linting

```bash
flake8 app tests
black app tests
```

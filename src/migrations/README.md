# Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) to manage PostgreSQL schema changes. Migration scripts are version-controlled under `src/migrations/versions/` and applied with the Alembic CLI.

## Configuration

Alembic reads the database connection from the `DATABASE_URL` environment variable (see `.env.example`). The value in `alembic.ini` is a placeholder; `env.py` converts async PostgreSQL URLs (`postgresql+asyncpg://`) to the synchronous driver (`postgresql+psycopg2://`) required by Alembic.

Set `DATABASE_URL` before running migration commands:

```bash
export DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

## Commands

| Command | Description |
|---------|-------------|
| `alembic upgrade head` | Apply all pending migrations |
| `alembic downgrade -1` | Roll back the most recent migration |
| `alembic downgrade base` | Roll back all migrations |
| `alembic current` | Show the current revision |
| `alembic history` | List migration history |
| `alembic revision --autogenerate -m "message"` | Generate a new revision from models |

## Version History

| Revision | Description |
|----------|-------------|
| `001_initial` | Initial schema: creates the `users` table |

## Initial Schema

The initial migration (`001_initial`) creates the `users` table with:

- `id` — UUID primary key
- `username` — unique, max 50 characters
- `email` — unique, max 255 characters
- `password_hash` — bcrypt hash, max 255 characters
- `created_at` — timezone-aware timestamp with server default
- `updated_at` — optional timezone-aware timestamp

## Rollback

All migrations define both `upgrade()` and `downgrade()` functions and are fully reversible.

- `alembic downgrade -1` — removes the most recent migration (drops `users` for the initial revision)
- `alembic downgrade base` — removes all migrations

Rolling back the initial migration drops the `users` table and permanently removes associated data. Use with caution outside development environments.

## Creating New Migrations

1. Update SQLAlchemy models in `src/api/models/`.
2. Ensure models are imported in `src/api/models/__init__.py` so autogenerate detects them.
3. Generate a revision: `alembic revision --autogenerate -m "describe change"`.
4. Review the generated script, then apply: `alembic upgrade head`.

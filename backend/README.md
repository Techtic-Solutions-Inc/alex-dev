# Backend API

FastAPI application foundation with PostgreSQL, Alembic migrations, JWT utilities, structured
error responses, CORS, request logging, rate limiting, and OpenAPI documentation.

## Local development

1. Copy `../.env.example` to `../.env` and set a high-entropy `JWT_SECRET`.
2. Install the project with its development dependencies.
3. From this directory, run `uvicorn app.main:app --reload`.

The API is available at `http://localhost:8000`; interactive documentation is at `/docs`.
`GET /health` and `GET /api/v1/health` both return the public health contract.

## Migrations

Run all Alembic commands from `backend/`:

```bash
alembic upgrade head
alembic revision --autogenerate -m "describe schema change"
```

Review generated migrations before applying them. Use a dedicated database configured through
`TEST_DATABASE_URL` for test or migration-validation workflows.

## API response contract

Successful responses use:

```json
{"success": true, "message": "Human-readable result.", "data": {}}
```

Errors use:

```json
{"success": false, "message": "UI-safe error.", "error": {"code": "STABLE_CODE", "details": null}}
```

Validation errors have status 422 and include field-level entries in `error.details`.

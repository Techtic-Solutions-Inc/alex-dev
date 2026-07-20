# Backend API

FastAPI backend with PostgreSQL, JWT authentication, Alembic migrations, structured logging, middleware, and pytest-based testing.

## Project Structure

```
├── alembic/                  # Database migrations
├── public/                   # Static assets served at /public
├── src/
│   ├── api/v1/
│   │   ├── controllers/      # HTTP controller layer
│   │   ├── models/           # Request/response Pydantic models
│   │   ├── routes/           # FastAPI route definitions
│   │   ├── services/         # Business logic
│   │   └── endpoints/        # Legacy endpoint modules
│   ├── config/               # Environment and app settings
│   ├── db/                   # SQLAlchemy engine and sessions
│   ├── middlewares/          # Auth, logging, CORS, rate limiting
│   ├── models/               # SQLAlchemy ORM models
│   ├── schemas/              # Backward-compatible schema re-exports
│   ├── utils/                # Shared utilities and error handling
│   ├── views/                # HTML/view helpers
│   └── main.py               # Application entry point
└── tests/
    ├── api/                  # API endpoint tests
    ├── e2e/                  # End-to-end workflow tests
    ├── integration/          # Integration tests
    └── unit/                 # Unit tests
```

## Requirements

- Python 3.11+
- PostgreSQL 14+ (SQLite is used automatically in tests)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` and update values:

| Variable | Description | Default |
|---|---|---|
| `ENVIRONMENT` | `development`, `testing`, or `production` | `development` |
| `DATABASE_URL` | SQLAlchemy database URL | PostgreSQL local URL |
| `JWT_SECRET_KEY` | Secret used to sign JWT tokens | _required in production_ |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes | `30` |
| `LOG_LEVEL` | Root log level | `INFO` |
| `CORS_ORIGINS` | Allowed CORS origins (JSON list) | `["*"]` |
| `RATE_LIMIT` | Default rate limit expression | `100/minute` |
| `SENDGRID_API_KEY` | SendGrid API key for email | empty |

Settings are loaded via `pydantic-settings` from environment variables and `.env`.

## Running the Application

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API documentation:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI schema: `http://localhost:8000/openapi.json`

## Database

The application uses SQLAlchemy with PostgreSQL in non-test environments.

Run migrations with Alembic:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "describe change"
```

## Authentication

Public routes:

- `GET /health`
- `POST /login`
- `POST /auth/register`
- `/docs`, `/redoc`, `/openapi.json`

Protected routes require a Bearer JWT token:

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/users/me
```

## Middleware Stack

1. **CORS** – cross-origin request handling
2. **Request logging** – logs request/response metadata and duration
3. **Request validation** – enforces JSON `Content-Type` for mutating requests
4. **JWT auth** – validates tokens for protected routes
5. **Rate limiting** – global limit via SlowAPI (disabled in testing)

## Error Handling

- `AppException` subclasses return structured `{ "error": { "message", "code", "details" } }` payloads
- Unhandled exceptions return HTTP 500 with a generic message and are logged

## Testing

```bash
pytest
```

Test categories:

- `tests/unit/` – isolated utility and service tests
- `tests/integration/` – API integration checks
- `tests/e2e/` – full user workflow tests
- `tests/test_setup.py` – setup validation (database, JWT middleware, logging)

Tests automatically use `ENVIRONMENT=testing`, in-memory SQLite, and disabled rate limiting.

## Linting and Formatting

```bash
black src tests
flake8 src tests
```

Configuration lives in `pyproject.toml` and `.flake8`.

## Public Assets

Static files in `public/` are served at `/public` (for example, `/public/status.json`).

# AI Assistant Backend

FastAPI backend for the AI Assistant module with user authentication.

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment variables (optional):

```bash
export DATABASE_URL=sqlite:///./app.db
export JWT_SECRET_KEY=your-secret-key
export SENDGRID_API_KEY=your-sendgrid-api-key
export SENDGRID_FROM_EMAIL=noreply@yourdomain.com
```

3. Run the application:

```bash
uvicorn src.main:app --reload
```

## API Endpoints

### POST `/api/v1/auth/register`

Register a new user with a unique email and strong password. Sends a confirmation email via SendGrid.

**Request body:**
```json
{
  "email": "user@example.com",
  "password": "StrongPass1!"
}
```

**Success (201):** Account created and confirmation email sent.

**Conflict (409):** `Email already in use. Please use a different email address.`

### POST `/api/v1/auth/login`

Authenticate with email and password to receive a JWT access token.

## Running Tests

```bash
pytest
```

## Database Migrations

Alembic is configured for database migrations:

```bash
alembic upgrade head
```

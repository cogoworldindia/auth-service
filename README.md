# Auth Service

FastAPI microservice responsible for authentication flows:

- Email OTP verification and login
- JWT access token validation
- Refresh token issuance and rotation (Redis-backed)

## Prerequisites

- Python 3.11+
- Poetry (recommended) or pip
- PostgreSQL database
- Redis instance

## Environment Variables

Copy `.env.example` to `.env` and set the following keys (sample values shown):

```
APP_PORT=8000
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/auth_service
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=super-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
REFRESH_TOKEN_REDIS_PREFIX=refresh_token:
EMAIL_SERVICE_URL=http://email-service
USER_SERVICE_URL=http://user-service
```

## Installation

```bash
poetry install
# or
pip install -r requirements.txt
```

## Database & Redis

Ensure PostgreSQL and Redis are running and accessible via the URLs provided in `.env`.

```bash
docker compose up -d postgres redis
```

Migrations run automatically on startup. To run manually:

```bash
alembic upgrade head
```

## Running the Service

```bash
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
# or
uvicorn app.main:app --reload
```

The API is served at `http://localhost:8000/v1/auth`.

## Tests

```bash
poetry run pytest -q
# or
pytest -q
```

Unit tests use dependency monkeypatching and bypass the application lifespan, so no external services are required.

## Key Endpoints

- `POST /v1/auth/email/send` – send OTP to email
- `POST /v1/auth/email/verify` – verify OTP, issue access + refresh tokens
- `GET /v1/auth/validate` – validate an access token (bearer header)
- `POST /v1/auth/token/refresh` – rotate refresh token and issue a new access token

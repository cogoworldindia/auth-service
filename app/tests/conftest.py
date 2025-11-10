import os
import contextlib
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _set_env():
    os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://user:pass@localhost:5432/testdb")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
    os.environ.setdefault("JWT_SECRET_KEY", "testsecret")
    os.environ.setdefault("JWT_ALGORITHM", "HS256")
    os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")
    os.environ.setdefault("EMAIL_SERVICE_URL", "http://email-service")
    os.environ.setdefault("USER_SERVICE_URL", "http://user-service")
    os.environ.setdefault("APP_PORT", "8000")
    yield


@pytest.fixture
def client(_set_env):
    # Import app after env is set
    from app.main import app

    @contextlib.asynccontextmanager
    async def noop_lifespan(_app):
        yield

    # Disable expensive startup/shutdown
    app.router.lifespan_context = noop_lifespan
    with TestClient(app) as c:
        yield c



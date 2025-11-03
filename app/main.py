from fastapi import FastAPI
from app.db import ensure_database_exists, run_migrations
from app.core.config import settings
from contextlib import asynccontextmanager
from app.controllers import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown lifecycle events."""
    database_url = settings.DATABASE_URL
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables.")

    # Ensure DB exists
    await ensure_database_exists(database_url)

    # Run Alembic migrations
    await run_migrations()

    yield  # App runs while inside this context

    print(" Shutting down, cleaning up resources...")


app = FastAPI(
    title="Auth Service",
    description="Handles authentication and token management",
    version="1.0.0",
)

# Include routers
app.include_router(api_router, prefix="/v1/auth", tags=["Authentication"])

# Health check route
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "auth_service"}

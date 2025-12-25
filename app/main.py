from fastapi import FastAPI
from app.db import ensure_database_exists, run_migrations, redis_client
from app.core.config import settings
from contextlib import asynccontextmanager
from app.controllers import router as api_router
import uvicorn
import app.core.firebase as initialize_firebase_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown lifecycle events."""
    database_url = settings.DATABASE_URL_SYNC
    if not database_url:
        raise ValueError("DATABASE_URL not found in environment variables.")
    print(" Starting up, initializing resources...1234567890")
    # Ensure DB exists
    ensure_database_exists(database_url)

    # Run Alembic migrations
    run_migrations()

    # Redis initialization 
    redis_client.init_redis()

    # Firebase initialization
    initialize_firebase_admin.initialize_firebase()

    yield  # App runs while inside this context

    # Shutdown: close Redis connection
    redis_client.close_redis()

    # print(" Shutting down, cleaning up resources...")


app = FastAPI(
    title="Auth Service",
    description="Handles authentication and token management",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(api_router, prefix="/v1/auth", tags=["Authentication"])

# Health check route
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "auth_service"}

# Entry point for running app
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(settings.APP_PORT),  # read from .env or settings
        reload=True
    )
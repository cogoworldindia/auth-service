import os
import subprocess
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from urllib.parse import urlparse


def ensure_database_exists(database_url: str):
    """Ensure the target database exists; if not, create it."""
    url = urlparse(database_url)
    db_name = url.path[1:]  # remove leading '/'
    default_url = f"{url.scheme}://{url.username}:{url.password}@{url.hostname}:{url.port or 5432}/authdb"

    default_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")

    try:
        with default_engine.connect() as conn:
            result = conn.execute(
                text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'")
            )
            exists = result.scalar() is not None
            if not exists:
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print(f"✅ Database '{db_name}' created.")
            else:
                print(f"✔ Database '{db_name}' already exists.")
    except OperationalError as e:
        print("❌ Could not connect to PostgreSQL. Is it running?")
        raise e


def run_migrations():
    """Run Alembic migrations automatically."""
    print("⚙ Running Alembic migrations...")
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("✅ Alembic migrations completed.")

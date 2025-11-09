from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_PORT: int = 8000
    DATABASE_URL: str
    REDIS_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    EMAIL_SERVICE_URL: str
    USER_SERVICE_URL: str

    class Config:
        env_file = ".env"

settings = Settings()

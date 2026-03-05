from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., validation_alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 1
    DATABASE_URL: str = Field(..., validation_alias="DB_URL")
    REDIS_URL: str = Field("redis://localhost:6379")
    SENTRY_DSN: str = Field("", validation_alias="SENTRY_DSN_PYTHON")

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DB_PORT: int
    SENTRY_DSN_NODE: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        env_ignore_empty=True,
        case_sensitive=True
    )

settings = Settings()
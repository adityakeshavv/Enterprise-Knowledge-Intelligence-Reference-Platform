import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "Nebula9 Enterprise Knowledge Intelligence"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"

    # Security
    SECRET_KEY: str = "nebula9-insecure-dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # Database - Default to /tmp in serverless/Vercel environments if not explicitly overridden
    DATABASE_URL: str = (
        f"sqlite:////tmp/nebula9_reference.db"
        if os.environ.get("VERCEL") or (Path("/tmp").is_dir() and not (BASE_DIR.parent / "nebula9_reference.db").exists())
        else f"sqlite:///{str((BASE_DIR.parent / 'nebula9_reference.db').resolve()).replace('\\', '/')}"
    )

    # Configurations
    CONFIG_DIR: str = str((BASE_DIR.parent / "config" / "industries").resolve())
    DEFAULT_INDUSTRY: str = "manufacturing"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

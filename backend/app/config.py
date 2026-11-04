import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

def resolve_database_url() -> str:
    # If running in Vercel or read-only container, SQLite MUST write to /tmp
    if os.environ.get("VERCEL"):
        return "sqlite:////tmp/nebula9_reference.db"
    
    # If explicit DATABASE_URL env var is provided, use it
    env_url = os.environ.get("DATABASE_URL")
    if env_url:
        return env_url
    
    # Check local candidates
    candidate1 = BASE_DIR / "nebula9_reference.db"
    candidate2 = BASE_DIR.parent / "nebula9_reference.db"
    if candidate1.exists():
        return f"sqlite:///{str(candidate1.resolve()).replace('\\', '/')}"
    elif candidate2.exists():
        return f"sqlite:///{str(candidate2.resolve()).replace('\\', '/')}"
    
    # Fallback to /tmp if write directory is unavailable
    if Path("/tmp").is_dir():
        return "sqlite:////tmp/nebula9_reference.db"
    
    return f"sqlite:///{str(candidate1.resolve()).replace('\\', '/')}"

def resolve_config_dir() -> str:
    candidate1 = BASE_DIR / "config" / "industries"
    candidate2 = BASE_DIR.parent / "config" / "industries"
    candidate3 = Path.cwd() / "backend" / "config" / "industries"
    candidate4 = Path.cwd() / "config" / "industries"
    for candidate in [candidate1, candidate2, candidate3, candidate4]:
        if candidate.exists():
            return str(candidate.resolve())
    return str(candidate1.resolve())

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

    # Database
    DATABASE_URL: str = resolve_database_url()

    # Configurations
    CONFIG_DIR: str = resolve_config_dir()
    DEFAULT_INDUSTRY: str = "manufacturing"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env") if (BASE_DIR / ".env").exists() and not os.environ.get("VERCEL") else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

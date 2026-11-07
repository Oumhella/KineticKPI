''''''
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "KineticKPI"
    app_env: str = "development"
    app_version: str = "0.1.0"
    database_url: str = "postgresql+psycopg://kinetickpi:kinetickpi_dev@localhost:5432/kinetickpi"
    upload_directory: Path = PROJECT_ROOT / "data" / "uploads"
    max_upload_size_mb: int = 20

    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()

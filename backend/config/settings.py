from pathlib import Path
from pydantic_settings import BaseSettings

# The .env file lives at the project root (one level above 'backend/')
_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    GEMINI_API_KEY: str
    QDRANT_URL: str = "https://your-qdrant-cluster.cloud.qdrant.io"
    QDRANT_API_KEY: str | None = None
    DATABASE_URL: str = "postgresql+asyncpg://USER:PASSWORD@YOUR_DB_HOST:5432/finance_db?sslmode=require"
    TRACER_BASE_URL: str = "https://www.oneoxyzen.com/api/tracers"
    TRACER_API_KEY: str = "fintech_191b6cbf190501150020a28fa04f94e3522668bce15c1dcdc330e955ef73c642"

    model_config = {
        "env_file": str(_ROOT / ".env"),
        "env_file_encoding": "utf-8",
    }


settings = Settings()

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(ENV_PATH)


@dataclass(slots=True)
class Settings:
    token: str
    prefix: str = "!"
    language: str = "vi"
    ai_enabled: bool = True
    database_path: str = str(BASE_DIR / "bot" / "database" / "bot.db")
    log_level: str = "INFO"



def get_settings() -> Settings:
    token = os.getenv("DISCORD_TOKEN", "")
    if not token:
        raise ValueError("Thiếu DISCORD_TOKEN trong file .env")

    return Settings(
        token=token,
        prefix=os.getenv("BOT_PREFIX", "!"),
        language=os.getenv("BOT_LANGUAGE", "vi"),
        ai_enabled=os.getenv("AI_ENABLED", "true").lower() == "true",
        database_path=os.getenv("DATABASE_PATH", str(BASE_DIR / "bot" / "database" / "bot.db")),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )

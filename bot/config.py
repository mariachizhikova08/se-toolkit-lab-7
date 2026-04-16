"""Configuration loader for the bot."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Загружаем .env файл
env_path = Path(__file__).parent.parent / ".env.bot.secret"
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    LMS_API_BASE_URL: str = os.getenv("LMS_API_BASE_URL", "http://127.0.0.1:42001")
    LMS_API_KEY: str = os.getenv("LMS_API_KEY", "lab7-secret-key-2026")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_API_BASE_URL: str = os.getenv(
        "LLM_API_BASE_URL", "http://10.93.25.242:42005/v1"
    )
    LLM_API_MODEL: str = os.getenv("LLM_API_MODEL", "qwen-coder")


settings = Settings()

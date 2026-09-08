"""
Idea Graveyard — Configuration
Single source of truth for all application settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/idea_graveyard"

    # AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash-lite"

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # App
    app_name: str = "Idea Graveyard"
    debug: bool = False

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()

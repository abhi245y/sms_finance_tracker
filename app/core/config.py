from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SMS Finance Tracker"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./finance_tracker.db"
    APP_SECRET_KEY: Optional[str] = None
    IPHONE_SHORTCUT_API_KEY: Optional[str] = None
    VERSION: str = "0.2.5"
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None
    MINI_APP_BASE_URL: Optional[str] = None
    TOKEN_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

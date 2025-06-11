from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SMS Finance Tracker"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./finance_tracker.db"
    APP_SECRET_KEY: str = secrets.token_hex(32)
    IPHONE_SHORTCUT_API_KEY: Optional[str] = None 
    VERSION: str = "0.1.4"
    
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
from pydantic_settings import BaseSettings
import secrets

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SMS Finance Tracker"
    SQLALCHEMY_DATABASE_URL: str = "sqlite:///./finance_tracker.db"
    APP_SECRET_KEY: str = secrets.token_hex(32)
    IPHONE_SHORTCUT_API_KEY: str = "1d3d5ea1d406e27b3586a7bb2e7f3d858223a61d1863c3fcdc03720085faae82"
    VERSION: str = "0.1.4"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
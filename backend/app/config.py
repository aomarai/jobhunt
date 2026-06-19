import os
from pathlib import Path
from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
class Settings(BaseSettings):
    database_url: PostgresDsn
    redis_url: RedisDsn
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Email
    mail_username: str
    mail_password: str
    mail_from: str
    mail_server: str
    mail_port: int = 587
    
    # API
    api_timeout: int = 10
    
    # Misc
    debug_mode: bool = False
    
    
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

settings = Settings() # pyright: ignore[reportCallIssue]
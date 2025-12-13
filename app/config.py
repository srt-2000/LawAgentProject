"""
Application configuration management.

This module handles environment variables and application settings
using Pydantic Settings for validation and type safety.
"""

import os

from passlib.context import CryptContext
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.config_schema import ResponseAuthDataDTO


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    SECRET_KEY: str
    ALGORITHM: str
    CRYPT_SCHEME: str
    ROUNDS: int
    SALT: int

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")
    )


settings = Settings()


def get_db_url() -> str:
    return (f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@"
            f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

def get_auth_data() -> ResponseAuthDataDTO:
    auth_data: dict[str, str] = {"secret_key": settings.SECRET_KEY, "algorithm": settings.ALGORITHM}
    return ResponseAuthDataDTO.model_validate(auth_data)

def get_pwd_context() -> CryptContext:
    pwd_context = CryptContext(
        schemes=settings.CRYPT_SCHEME.split(","),
        bcrypt__rounds=settings.ROUNDS,
        bcrypt__salt_size=settings.SALT,
        deprecated="auto"
    )
    return pwd_context
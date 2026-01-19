"""
Application configuration management.

This module handles environment variables and application settings
using Pydantic Settings for validation and type safety.
"""

from typing import Literal

from fastapi.exceptions import ValidationException
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.config_schema import AuthConfigDTO


class BaseAppSettings(BaseSettings):
    """Base settings class with common configuration."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class DatabaseSettings(BaseAppSettings):
    """Database connection settings."""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @field_validator("DB_PORT")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate database port is in valid range.

        Args:
            v: Port number to validate.

        Returns:
            int: Validated port number.

        Raises:
            ValueError: If port is not in valid range (1-65535).
        """
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v

    @computed_field  # type: ignore[prop-decorator]
    def db_url(self) -> str:
        """Construct database connection URL from settings.

        Returns:
            str: PostgreSQL async connection URL.
        """
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


class AuthSettings(BaseAppSettings):
    """Authentication settings."""

    SECRET_KEY: str
    ALGORITHM: Literal["HS256", "HS384", "HS512"]
    ROUNDS: int

    @field_validator("ROUNDS")
    @classmethod
    def validate_rounds(cls, v: int) -> int:
        """Validate bcrypt rounds are in valid range.

        Args:
            v: BCrypt rounds to validate.

        Returns:
            int: Validated rounds number.

        Raises:
            ValueError: If rounds are not in valid range (4-31).
        """
        if not 4 <= v <= 31:
            raise ValueError("BCrypt rounds must be between 4 and 31")
        return v

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key is not empty and has minimum length.

        Args:
            v: Secret key to validate.

        Returns:
            str: Validated secret key.

        Raises:
            ValueError: If secret key is empty or too short (less than 32 characters).
        """
        if not v or len(v) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        return v

    @computed_field  # type: ignore[prop-decorator]
    def auth_config(self) -> AuthConfigDTO:
        """Get authentication configuration data.

        Returns:
            AuthConfigDTO: Authentication data containing secret key and algorithm.
        """
        return AuthConfigDTO(
            secret_key=self.SECRET_KEY,
            algorithm=self.ALGORITHM,
        )


class Settings(BaseAppSettings):
    """Application settings loaded from environment variables."""

    database: DatabaseSettings
    auth: AuthSettings
    WELCOME_MESSAGE: str = "Hello! How can I help you?"


def get_settings() -> Settings:
    """Initialize and return application settings.

    Returns:
        Settings: Validated application settings.

    Raises:
        ValidationException: If required environment variables are missing or invalid.
    """
    try:
        project_settings = Settings(database=DatabaseSettings(), auth=AuthSettings())
    except ValidationException as er:
        for env_error in er.errors():
            env_name = env_error["loc"][0] if env_error["loc"] else "unknown"
            env_msg = env_error["msg"]
            print(f"Configuration error in '{env_name}': {env_msg}")
        raise
    else:
        return project_settings


settings = get_settings()

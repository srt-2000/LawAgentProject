"""
Application configuration management.

This module handles environment variables and application settings
using Pydantic Settings for validation and type safety.
"""

from typing import Literal

from loguru import logger
from fastapi.exceptions import ValidationException
from pydantic import field_validator, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.schemas.config import AuthConfigDataDomain
from app.constants import (
    ConfigFields,
    ConfigMessages,
    ConfigPaths, IGNORE, MIN_PORT_NUMBER, MAX_PORT_NUMBER, MIN_ROUNDS_NUMBER, MAX_ROUNDS_NUMBER, MAX_SECRET_KEY_LEN
)


class BaseAppSettings(BaseSettings):
    """Base for all settings classes. Loads from .env and ignores extra keys."""

    model_config = SettingsConfigDict(
        env_file=ConfigPaths.ENV_FILE_NAME, extra=IGNORE
    )


class DatabaseSettings(BaseAppSettings):
    """Database connection settings (host, port, name, credentials)."""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    @field_validator(ConfigFields.DB_PORT)
    @classmethod
    def validate_port(cls, port_number: int) -> int:
        """Validate database port is in valid range.

        Args:
            port_number: Port number to validate.

        Returns:
            int: Validated port number.

        Raises:
            ValueError: If port is not in valid range (1-65535).
        """
        if (
            not MIN_PORT_NUMBER
                <= port_number
                <= MAX_PORT_NUMBER
        ):
            raise ValueError(ConfigMessages.PORT_NUMBER_VALUE_ERROR)
        return port_number

    @computed_field  # type: ignore[prop-decorator]
    def db_url(self) -> str:
        """Build async PostgresSQL connection URL from environment settings.

        Returns:
            str: Async connection URL for SQLAlchemy (postgresql+asyncpg).
        """
        return (
            f"{ConfigPaths.POSTGRESQL_ASYNCPG_LINK_BEGIN}"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


class RedisSettings(BaseAppSettings):
    """Redis connection settings (host, port, database, credentials)."""

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: str

    @computed_field
    def redis_url(self) -> str:
        """Build Redis connection URL from environment settings.

        Returns:
            str: Redis URL of the form "redis://:<password>@<host>:<port>/<db>".
        """
        return f"{ConfigPaths.REDIS_LINK_BEGIN}{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


class AuthSettings(BaseAppSettings):
    """Authentication settings: JWT secret, algorithm, and bcrypt rounds."""

    ACCESS_SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    REFRESH_TOKEN_ENTROPY: int
    ALGORITHM: Literal["HS256", "HS384", "HS512"]
    ACCESS_TOKEN_EXP_TIME_MINUTES: float
    REFRESH_TOKEN_EXP_TIME_HOURS: float
    ROUNDS: int

    @field_validator(ConfigFields.CRYPT_ROUNDS)
    @classmethod
    def validate_rounds(cls, rounds_number: int) -> int:
        """Validate bcrypt rounds are in valid range.

        Args:
            rounds_number: BCrypt rounds to validate.

        Returns:
            int: Validated rounds number.

        Raises:
            ValueError: If rounds are not in valid range (4-31).
        """
        if (
            not MIN_ROUNDS_NUMBER
                <= rounds_number
                <= MAX_ROUNDS_NUMBER
        ):
            raise ValueError(ConfigMessages.CRYPT_ROUNDS_VALUE_ERROR)
        return rounds_number

    @field_validator(
        ConfigFields.ACCESS_SECRET_KEY, ConfigFields.REFRESH_SECRET_KEY
    )
    @classmethod
    def validate_secret_key(cls, secret_key: str) -> str:
        """Validate secret key is not empty and has minimum length.

        Args:
            secret_key: Secret key to validate.

        Returns:
            str: Validated secret key.

        Raises:
            ValueError: If secret key is empty or too short (less than 32 characters).
        """
        if not secret_key or len(secret_key) < MAX_SECRET_KEY_LEN:
            raise ValueError(ConfigMessages.SECRET_KEY_VALUE_ERROR)
        return secret_key

    @computed_field  # type: ignore[prop-decorator]
    def auth_config(self) -> AuthConfigDataDomain:
        """Build validated JWT configuration for token services.

        Returns:
            AuthConfigDataDomain: Access and refresh secrets, algorithm, entropy, and
                token lifetimes derived from environment settings.
        """
        return AuthConfigDataDomain(
            access_secret_key=self.ACCESS_SECRET_KEY,
            refresh_secret_key=self.REFRESH_SECRET_KEY,
            refresh_token_entropy=self.REFRESH_TOKEN_ENTROPY,
            algorithm=self.ALGORITHM,
            access_token_exp_time_minutes=self.ACCESS_TOKEN_EXP_TIME_MINUTES,
            refresh_token_exp_time_hours=self.REFRESH_TOKEN_EXP_TIME_HOURS,
        )


class Settings(BaseAppSettings):
    """Application settings loaded from environment variables."""

    database: DatabaseSettings
    auth: AuthSettings
    redis: RedisSettings


def get_settings() -> Settings:
    """Initialize and return application settings.

    Returns:
        Settings: Validated application settings.

    Raises:
        ValidationException: If required environment variables are missing or invalid.
    """
    try:
        project_settings = Settings(
            database=DatabaseSettings(), auth=AuthSettings(), redis=RedisSettings()
        )
    except ValidationException as er:
        for env_error in er.errors():
            env_name: str
            env_msg: str

            if env_error[ConfigFields.LOC]:
                env_name = env_error[ConfigFields.LOC][0]
            else:
                env_name = ConfigMessages.ENV_ERROR_UNKNOWN

            env_msg = env_error[ConfigFields.ENV_ERROR_MESSAGE]
            logger.error(f"{ConfigMessages.CONFIG_ERROR} '{env_name}': {env_msg}")
        raise
    else:
        return project_settings


settings = get_settings()

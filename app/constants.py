"""Constants for Config fields, values and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from typing import Literal

POSTGRESQL_ASYNCPG_LINK_BEGIN: str = "postgresql+asyncpg://"
REDIS_LINK_BEGIN: str = "redis://:"


class ConfigFieldNames:
    """Environment variable names used by settings validators."""

    DB_PORT: str = "DB_PORT"
    CRYPT_ROUNDS: str = "ROUNDS"
    ACCESS_SECRET_KEY: str = "ACCESS_SECRET_KEY"
    REFRESH_SECRET_KEY: str = "REFRESH_SECRET_KEY"


class ConfigValues:
    """Constraints and default values for configuration parsing."""

    MIN_PORT_NUMBER: int = 1
    MAX_PORT_NUMBER: int = 65535
    MIN_ROUNDS_NUMBER: int = 4
    MAX_ROUNDS_NUMBER: int = 31
    MAX_SECRET_KEY_LEN: int = 32
    ENV_FILE_NAME: str = ".env"
    IGNORE: Literal["ignore"] = "ignore"


class ConfigMessages:
    """User-facing error messages for configuration validation."""

    PORT_NUMBER_VALUE_ERROR: str = "Port must be between 1 and 65535"
    CRYPT_ROUNDS_VALUE_ERROR: str = "BCrypt rounds must be between 4 and 31"
    SECRET_KEY_VALUE_ERROR: str = (
        f"Secret key and Refresh secret key must be "
        f"at least {ConfigValues.MAX_SECRET_KEY_LEN} "
        f"characters long"
    )
    CONFIG_ERROR: str = "Configuration error"
    ENV_ERROR_UNKNOWN: str = "Unknown env constants validation error"


class EnvErrorsFieldNames:
    """Keys used by Pydantic validation error dictionaries."""

    LOC: str = "loc"
    ENV_ERROR_MESSAGE: str = "msg"


class FieldNames:
    """Standard field names used in API error payloads."""

    DETAIL: str = "detail"


class FieldValues:
    """Standard values used across routers and clients."""

    MAIN_PATH_NAME: str = "/"
    PROFILE_PATH_NAME: str = "/profile"
    LOGIN_PATH_NAME: str = "/login"
    GET_HTTP_METHOD_NAME: str = "GET"

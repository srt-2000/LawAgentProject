"""Constants for Config fields, values and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from typing import Literal

POSTGRESQL_ASYNCPG_LINK_BEGIN: str = "postgresql+asyncpg://"
REDIS_LINK_BEGIN: str = "redis://:"


class BaseConstants:
    """Common using constants."""

    USER_DISABLED: str = "User is disabled"
    MESSAGE_FIELD: str = "message"
    USER_ID: str = "user_id"
    ID: str = "id"


class ConfigFieldNames:
    DB_PORT: str = "DB_PORT"
    CRYPT_ROUNDS: str = "ROUNDS"
    SECRET_KEY: str = "SECRET_KEY"


class ConfigValues:
    MIN_PORT_NUMBER: int = 1
    MAX_PORT_NUMBER: int = 65535
    MIN_ROUNDS_NUMBER: int = 4
    MAX_ROUNDS_NUMBER: int = 31
    MAX_SECRET_KEY_LEN: int = 32
    ENV_FILE_NAME: str = ".env"
    IGNORE: Literal["ignore"] = "ignore"


class ConfigMessages:
    PORT_NUMBER_VALUE_ERROR: str = "Port must be between 1 and 65535"
    CRYPT_ROUNDS_VALUE_ERROR: str = "BCrypt rounds must be between 4 and 31"
    SECRET_KEY_VALUE_ERROR: str = "Secret key must be at least 32 characters long"
    CONFIG_ERROR: str = "Configuration error"
    ENV_ERROR_UNKNOWN: str = "Unknown env constants validation error"


class EnvErrorsFieldNames:
    LOC: str = "loc"
    ENV_ERROR_MESSAGE: str = "msg"


class FieldNames:
    DETAIL: str = "detail"


class FieldValues:
    MAIN_PATH_NAME: str = "/"
    PROFILE_PATH_NAME: str = "/profile"
    LOGIN_PATH_NAME: str = "/login"
    GET_HTTP_METHOD_NAME: str = "GET"

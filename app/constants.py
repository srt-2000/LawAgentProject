"""Constants for Config fields, values and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from enum import StrEnum
from typing import Literal


GET: Literal["GET"] = "GET"
IGNORE: Literal["ignore"] = "ignore"
MIN_PORT_NUMBER = 1
MAX_PORT_NUMBER = 65535
MIN_ROUNDS_NUMBER = 4
MAX_ROUNDS_NUMBER = 31
MAX_SECRET_KEY_LEN = 32


class ConfigFields(StrEnum):
    """Environment variable names."""

    DB_PORT = "DB_PORT"
    CRYPT_ROUNDS = "ROUNDS"
    ACCESS_SECRET_KEY = "ACCESS_SECRET_KEY"
    REFRESH_SECRET_KEY = "REFRESH_SECRET_KEY"
    DETAIL = "detail"
    LOC = "loc"
    ENV_ERROR_MESSAGE = "msg"


class ConfigMessages(StrEnum):
    """User-facing error messages for configuration validation."""

    PORT_NUMBER_VALUE_ERROR = "Port must be between 1 and 65535"
    CRYPT_ROUNDS_VALUE_ERROR = "BCrypt rounds must be between 4 and 31"
    SECRET_KEY_VALUE_ERROR = "Secret key or Refresh secret key is not valid "
    CONFIG_ERROR = "Configuration error"
    ENV_ERROR_UNKNOWN = "Unknown env constants validation error"


class ConfigPaths(StrEnum):
    """Standard values used across routers and clients."""

    ROOT = "/"
    PROFILE = "/profile"
    LOGIN = "/login"
    POSTGRESQL_ASYNCPG_LINK_BEGIN = "postgresql+asyncpg://"
    REDIS_LINK_BEGIN = "redis://:"
    ENV_FILE_NAME = ".env"

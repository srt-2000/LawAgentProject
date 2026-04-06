"""Constants for Services fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from typing import Final


class StandardMessages:
    """Standard messages from services."""

    WS_ERROR_MESSAGE: str = "Websocket ERROR"
    SEND_MESSAGE_ERROR: str = "Send message error"
    SAVE_MESSAGE_TO_DB_ERROR: str = "Save message to DB error"
    SERIALIZE_MESSAGE_ERROR: str = "Serialize message before sending error"
    RECEIVE_MESSAGE_ERROR: str = "Receive message error"
    REFRESH_TOKEN_REDIS_ERROR: str = "Refresh token REDIS error"
    REFRESH_TOKEN_IS_NOT_VALID: str = "Refresh token NOT VALID"
    NEW_CHAT_OF: str = "new chat of"
    USER_NOT_FOUND: str = "user not found"
    CHAT_NOT_FOUND: str = "chat not found"
    TOKEN_NOT_VALID: str = "Token is not valid"
    TOKEN_IS_EXPIRED: str = "Token is expired"


class FieldNames:
    """Standard fields names for services."""

    TITLE: str = "title"
    TOKEN_SUB: str = "sub"
    TOKEN_EXP: str = "exp"
    EMAIL: str = "email"


class FieldsValues:
    """Standard fields values for services."""

    USERS_ACCESS_TOKEN: str = "users_access_token"
    EMPTY_STRING: str = ""
    UTF_8: str = "utf-8"
    REFRESH_KEY_PREFIX: Final[str] = "rt:"
    TOKEN_SEPARATOR: Final[str] = "."
    CONCAT_SEPARATOR: str = "|"
    SID_BYTES_QUERY: int = 16
    SECRET_BYTES_QUERY: int = 32

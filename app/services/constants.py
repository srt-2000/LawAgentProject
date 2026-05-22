"""Constants for Services fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from enum import StrEnum
from typing import Literal


# TOKENS names
USERS_ACCESS_TOKEN: str = "users_access_token"
USERS_REFRESH_TOKEN: str = "users_refresh_token"

# STRICT values
UTF_8: Literal["utf-8"] = "utf-8"
REFRESH: Literal["refresh"] = "refresh"


class Messages(StrEnum):
    """Standard messages from services."""

    WS_ERROR_MESSAGE = "Websocket ERROR"
    WS_DISCONNECTED = "Websocket disconnected"
    SEND_MESSAGE_ERROR = "Send message error"
    SAVE_MESSAGE_TO_DB_ERROR = "Save message to DB error"
    SERIALIZE_MESSAGE_ERROR = "Serialize message before sending error"
    RECEIVE_MESSAGE_ERROR = "Receive message error"
    REFRESH_TOKEN_REDIS_ERROR = "Refresh token REDIS error"
    REFRESH_TOKEN_IS_NOT_VALID = "Refresh token NOT VALID"
    REFRESH_TOKEN_DECODE_ERROR = "Refresh token decode error"
    REVOKE_REFRESH_TOKEN_ERROR = "Revoke refresh token error"
    INVALID_TOKEN_TYPE = "Invalid token type"
    USER_ID_DONT_MATCH = "User ID in refresh token and in the storage dont match"
    USER_DISABLED = "User disabled"
    PASSWORD_DOESNT_MATCH = "Password doesn't match"
    NEW_CHAT_OF = "new chat of"
    USER_NOT_FOUND = "user not found"
    ACCESS_TOKEN_DECODE_ERROR = "Access token decode error"
    TOKEN_NOT_VALID = "Token is not valid"
    TOKEN_IS_EXPIRED = "Token is expired"
    TOKEN_EXPIRATION_IS_NONE = "Token expiration isn't none"
    TOKEN_NOT_FOUND = "Token not found"
    AUTH_DATA_NOT_CORRECT = "Auth data not correct"


class Fields(StrEnum):
    """Standard fields names for services."""

    TITLE = "title"
    TOKEN_SUB = "sub"
    TOKEN_EXP = "exp"
    REFRESH_TOKEN_JTI = "jti"
    REFRESH_TOKEN_TYPE = "typ"
    EMAIL = "email"
    MESSAGE = "message"
    ID = "id"
    USER_ID = "user_id"

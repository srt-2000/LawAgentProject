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
    NEW_CHAT_OF = "new chat of"
    USER_NOT_FOUND = "user not found"
    TOKEN_NOT_VALID = "Token is not valid"
    TOKEN_IS_EXPIRED = "Token is expired"


class Fields(StrEnum):
    """Standard fields names for services."""

    TITLE = "title"
    TOKEN_SUB = "sub"
    TOKEN_EXP = "exp"
    REFRESH_TOKEN_JTI = "jti"
    REFRESH_TOKEN_TYPE = "typ"
    EMAIL = "email"
    MESSAGE = "message"

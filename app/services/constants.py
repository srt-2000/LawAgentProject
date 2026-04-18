"""Constants for Services fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from typing import Literal


class StandardMessages:
    """Standard messages from services."""

    WS_ERROR_MESSAGE: str = "Websocket ERROR"
    SEND_MESSAGE_ERROR: str = "Send message error"
    SAVE_MESSAGE_TO_DB_ERROR: str = "Save message to DB error"
    SERIALIZE_MESSAGE_ERROR: str = "Serialize message before sending error"
    RECEIVE_MESSAGE_ERROR: str = "Receive message error"
    REFRESH_TOKEN_REDIS_ERROR: str = "Refresh token REDIS error"
    REFRESH_TOKEN_IS_NOT_VALID: str = "Refresh token NOT VALID"
    REFRESH_TOKEN_DECODE_ERROR: str = "Refresh token decode error"
    REVOKE_REFRESH_TOKEN_ERROR: str = "Revoke refresh token error"
    INVALID_TOKEN_TYPE: str = "Invalid token type"
    USER_ID_DONT_MATCH: str = "User ID in refresh token and in the storage dont match"
    NEW_CHAT_OF: str = "new chat of"
    USER_NOT_FOUND: str = "user not found"
    TOKEN_NOT_VALID: str = "Token is not valid"
    TOKEN_IS_EXPIRED: str = "Token is expired"


class FieldNames:
    """Standard fields names for services."""

    TITLE: str = "title"
    TOKEN_SUB: str = "sub"
    TOKEN_EXP: str = "exp"
    REFRESH_TOKEN_JTI: str = "jti"
    REFRESH_TOKEN_TYPE: str = "typ"
    EMAIL: str = "email"


class FieldValues:
    """Standard fields values for services."""

    USERS_ACCESS_TOKEN: str = "users_access_token"
    USERS_REFRESH_TOKEN: str = "users_refresh_token"
    UTF_8: str = "utf-8"
    REFRESH: Literal["refresh"] = "refresh"

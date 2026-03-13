"""Constants for API fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""


class RouterFieldNames:
    """Standard field names used in API payloads."""

    PASSWORD_CONFIRM: str = "password_confirm"
    PASSWORD_HASH: str = "password_hash"
    PASSWORD: str = "password"
    MESSAGE_FIELD: str = "message"
    OK: str = "ok"
    ACCESS_TOKEN: str = "access_token"
    REFRESH_TOKEN: str = "refresh_token"
    CHAT_ID: str = "chat_id"


class RouterStandardMessages:
    """Standard user-facing text messages."""

    WELCOME_MESSAGE: str = "Hello! How can I help you?"
    INVALID_CHAT:str = "Invalid chat_id"
    CHAT_NOT_FOUND: str = "Chat not found"
    STUB_MESSAGE: str = "STUB test message sent/receive"
    AUTH_SUCCESS: str = "Authorisation successful"
    LOGOUT_MESSAGE: str = "User is logout"


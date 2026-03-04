"""Constants for API fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""


class FieldNames:
    """Standard field names used in API payloads."""

    PASSWORD_CONFIRM: str = "password_confirm"
    PASSWORD_HASH: str = "password_hash"
    PASSWORD: str = "password"
    MESSAGE_FIELD: str = "message"
    OK: str = "ok"
    ACCESS_TOKEN: str = "access_token"
    REFRESH_TOKEN: str = "refresh_token"


class StandardMessages:
    """Standard user-facing text messages."""

    WELCOME_MESSAGE: str = "Hello! How can I help you?"

"""Constants for API fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from typing import Literal


class RouterFieldNames:
    """Standard field names used in API payloads."""

    PASSWORD_CONFIRM: str = "password_confirm"
    PASSWORD_HASH: str = "password_hash"
    PASSWORD: str = "password"
    OK: str = "ok"
    ACCESS_TOKEN: str = "access_token"
    REFRESH_TOKEN: str = "refresh_token"
    CHAT_ID: str = "chat_id"
    ID: str = "id"
    REQUEST: str = "request"
    PROFILE: str = "profile"


class FieldValues:
    """Standard field values used in API payloads."""

    USERS_ACCESS_TOKEN: str = "users_access_token"
    LAX: Literal["lax"] = "lax"
    ROOT_PATH: str = "/"
    TEMPLATES_PATH: str = "app/templates"
    USER_TAG: str = "User"
    CHATS_TAG: str = "Chats"
    PAGES_TAG: str = "Pages"
    INDEX_HTML: str = "index.html"
    PROFILE_HTML: str = "profile.html"
    LOGIN_HTML: str = "login.html"


class RouterStandardMessages:
    """Standard user-facing text messages."""

    # AUTH messages
    AUTH_DATA_NOT_CORRECT: str = "Login or Password is not right"
    AUTH_SUCCESS: str = "Authorisation successful"
    LOGOUT_MESSAGE: str = "User is logout"

    # USER messages
    USER_REGISTERED: str = "user registered successfully"
    USER_IS_EXIST: str = "User is already exist"
    USER_NOT_FOUND: str = "User not found"
    USER_NOT_DISABLED: str = "User not disabled"

    # CHAT messages
    WELCOME_MESSAGE: str = "Hello! How can I help you?"
    INVALID_CHAT: str = "Invalid chat_id"
    CHAT_NOT_FOUND: str = "Chat not found"
    STUB_MESSAGE: str = "STUB test message sent/receive"
    CHATS_DELETED: str = "chats deleted"

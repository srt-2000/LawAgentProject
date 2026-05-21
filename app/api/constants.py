"""Constants for API fields, values and default messages.

This module centralizes commonly used constant values
to avoid magic strings across the codebase.
"""

from enum import StrEnum
from typing import Literal


REASON_LEN_LIMIT: int = 123
LAX: Literal["lax"] = "lax"
ROOT_PATH: str = "/"
TEMPLATES_PATH: str = "app/templates"
INDEX_HTML: str = "index.html"
PROFILE_HTML: str = "profile.html"
LOGIN_HTML: str = "login.html"


class Fields(StrEnum):
    """Standard field names used in API payloads."""

    PASSWORD_CONFIRM = "password_confirm"
    PASSWORD_HASH = "password_hash"
    PASSWORD = "password"
    OK = "ok"
    ACCESS_TOKEN = "access_token"
    CHAT_ID = "chat_id"
    USER_ID = "user_id"
    ID = "id"
    REQUEST = "request"
    PROFILE = "profile"
    MESSAGE = "message"


class Values(StrEnum):
    """Standard field values used in API payloads."""

    USERS_ACCESS_TOKEN = "users_access_token"
    USERS_REFRESH_TOKEN = "users_refresh_token"
    USER_TAG = "User"
    CHATS_TAG = "Chats"
    PAGES_TAG = "Pages"


class Messages(StrEnum):
    """Standard user-facing text messages."""

    # AUTH messages
    AUTH_DATA_NOT_CORRECT = "Auth data not correct"
    AUTH_SUCCESS = "Authorisation successful"
    LOGOUT_MESSAGE = "User is logout"
    ACCESS_TOKEN_REFRESHED = "Access token refreshed"
    NOT_EXPECTED_AUTH_ERROR = "Not expected authenticate error"

    # USER messages
    USER_REGISTERED = "user registered successfully"
    USER_IS_EXIST = "User is already exist"
    USER_NOT_FOUND = "User not found"
    USER_DISABLED = "User is disabled"
    DISABLE_FAILED = "Disable failed"

    # CHAT messages
    WELCOME_MESSAGE = "Hello! How can I help you?"
    INVALID_CHAT = "Invalid chat_id"
    CHAT_NOT_FOUND = "Chat not found"
    STUB_MESSAGE = "STUB test message sent/receive"
    CHATS_DELETED = "chats deleted"
    WS_ERROR_MESSAGE = "Websocket ERROR"

    # DEPENDENCIES messages
    NO_USER_ID_IN_TOKEN = "No user id found in token"
    USER_IS_NOT_ACTIVE = "User is not active"
    ERROR_GET_WS_ACTIVE_USER = "Error while getting active user from websocket"
    SESSION_FAILED = "Session failed"

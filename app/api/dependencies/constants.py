"""Constants for Dependencies fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""


class DependencyMessages:
    """User-facing and log messages for dependency-layer auth flows."""

    USER_NOT_FOUND: str = "User not found"
    NO_USER_ID_IN_TOKEN: str = "No user id found in token"
    USER_IS_NOT_ACTIVE: str = "User is not active"
    ERROR_GET_WS_ACTIVE_USER: str = "Error while getting active user from websocket"


class Values:
    """Numeric limits and helpers for dependency implementations."""

    REASON_LEN_LIMIT: int = 123

"""Constants for Dependencies fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""


class DependencyMessages:
    """Standard field names used in Dependencies payloads."""

    TOKEN_NOT_VALID: str = "Token is not valid"
    TOKEN_IS_EXPIRED: str = "Token is expired"
    USER_NOT_FOUND: str = "User not found"


class FieldValues:
    """Standard field values used in Dependencies payloads."""

    USERS_ACCESS_TOKEN: str = "users_access_token"

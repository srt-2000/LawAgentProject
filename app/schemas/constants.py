"""Constants for Schemas fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from typing import Literal


class FieldNames:
    """Standard field names used in Schemas payloads."""

    TITLE: str = "title"


class FieldValues:
    """Standard field values used in Schemas payloads."""

    BEFORE_MODE: Literal["before"] = "before"
    AFTER_MODE: Literal["after"] = "after"
    NAME_FIELD_DESCRIPTION: str = "Display name, 2 to 50 characters"
    EMAIL_FIELD_DESCRIPTION: str = "Email"
    PASS_FIELD_DESCRIPTION: str = "Password, 6 to 50 characters"
    PASS_CONFIRM_DESCRIPTION: str = "Must match password"
    EMAIL_EXAMPLE: str = "user@example.com"
    FORBID_VALUE: Literal["forbid"] = "forbid"
    REFRESH: Literal["refresh"] = "refresh"
    NAME_MIN_LEN: int = 2
    EMAIL_MIN_LEN: int = 6
    PASS_MIN_LEN: int = 6
    MAX_FIELD_LEN: int = 50


class StandardMessages:
    """Standard message values used in Schemas payloads."""

    PASSWORDS_NOT_MATCH: str = "Passwords do not match"
    PASS_CONFIRM_REQUIRE: str = "Both password and password confirm must be provided"

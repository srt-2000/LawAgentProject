"""Constants for Schemas fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from enum import StrEnum
from typing import Literal


# FIELDS names
TITLE: str = "title"

# VALUES
BEFORE_MODE: Literal["before"] = "before"
AFTER_MODE: Literal["after"] = "after"
FORBID_VALUE: Literal["forbid"] = "forbid"
NAME_MIN_LEN: int = 2
PASS_MIN_LEN: int = 6
MAX_FIELD_LEN: int = 50


class Descriptions(StrEnum):
    """Standard field values used in Schemas payloads."""

    NAME_FIELD_DESCRIPTION = "Display name, 2 to 50 characters"
    EMAIL_FIELD_DESCRIPTION = "Email"
    PASS_FIELD_DESCRIPTION = "Password, 6 to 50 characters"
    PASS_CONFIRM_DESCRIPTION = "Must match password"
    EMAIL_EXAMPLE = "user@example.com"


class Messages(StrEnum):
    """Standard message values used in Schemas payloads."""

    PASSWORDS_NOT_MATCH = "Passwords do not match"
    PASS_CONFIRM_REQUIRE = "Both password and password confirm must be provided"

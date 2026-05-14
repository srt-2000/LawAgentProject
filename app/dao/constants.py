"""Constants for DAO fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""

from enum import StrEnum


# FIELDS names
ROWCOUNT = "rowcount"
KEY = "key"

# VALUES
KEY_VALUE: str = "KEY_VALUE"
ID: str = "id"


class Messages(StrEnum):
    """Standard messages used in DAO payloads."""

    OBJECT_NOT_FOUND = "object not found"
    DATA_IS_NONE = "data is NONE"
    UPDATE_FAILED = "update failed"
    SAVING_FAILED = "saving failed"
    GET_DEL_OPERATION_FAILED = "redis get/del operation failed"

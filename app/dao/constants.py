"""Constants for DAO fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""


class DAOFieldNames:
    """Standard field values used in DAO payloads."""

    ROWCOUNT: str = "rowcount"
    KEY: str = "key"


class DAOStandardMessages:
    """Standard messages used in DAO payloads."""

    OBJECT_NOT_FOUND: str = "object not found"
    DATA_IS_NONE: str = "data is NONE"
    UPDATE_FAILED: str = "update failed"
    SAVING_FAILED: str = "saving failed"
    READING_FAILED: str = "reading from storage failed"
    DELETE_FAILED: str = "delete failed"


class DAOFieldValues:
    """Standard field values used in DAO payloads."""

    KEY_VALUE: str = "KEY_VALUE"

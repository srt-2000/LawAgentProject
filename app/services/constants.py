"""Constants for Services fields and default messages.

This module centralizes commonly used constant values for request and
response payloads to avoid magic strings across the codebase.
"""


class StandardMessages:
    """Standard messages from services."""

    WS_ERROR_MESSAGE: str = "Websocket ERROR"
    SEND_MESSAGE_ERROR: str = "Send message error"
    SAVE_MESSAGE_TO_DB_ERROR: str = "Save message to DB error"
    SERIALIZE_MESSAGE_ERROR: str = "Serialize message before sending error"
    RECEIVE_MESSAGE_ERROR: str = "Receive message error"
    NEW_CHAT_OF: str = "new chat of"
    USER_NOT_FOUND: str = "user not found"
    CHAT_NOT_FOUND: str = "chat not found"


class FieldNames:
    """Standard fields names for services."""

    TITLE: str = "title"
    TOKEN_SUB: str = "sub"
    TOKEN_EXP: str = "exp"


class FieldsValues:
    """Standard fields values for services."""

    EMPTY_STRING: str = ""
    UTF_8: str = "utf-8"
    EXP_DELTA_TIME: int = 5

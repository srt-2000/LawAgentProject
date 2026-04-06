from app.dao.constants import DAOStandardMessages


class ObjectNotFoundException(Exception):
    """Raised when expected DB object is not found."""

    def __init__(self, model_name: str) -> None:
        """Initialize ObjectNotFoundException.

        Args:
            model_name: Name of model that was not found.
        """

        self.model_name: str = model_name
        super().__init__(f"{model_name} {DAOStandardMessages.OBJECT_NOT_FOUND}")


class RedisKeyValueNotFoundException(Exception):
    """Raised when expected Redis key_value is not found."""

    def __init__(self, record_type_name: str) -> None:
        """Initialize KeyValueNotFoundException.

        Args:
            record_type_name: Name of record type that was not found.
        """

        self.record_type_name: str = record_type_name
        super().__init__(f"{record_type_name} {DAOStandardMessages.DATA_IS_NONE}")

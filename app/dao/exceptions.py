


class ObjectNotFoundException(Exception):
    """Raised when expected DB object is not found."""

    def __init__(self, model_name: str) -> None:
        """Initialize ObjectNotFoundException.

        Args:
            model_name: Name of model that was not found.
        """

        self.model_name: str = model_name
        super().__init__(f"{model_name} object not found")


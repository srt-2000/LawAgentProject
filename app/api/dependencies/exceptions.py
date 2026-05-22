"""Domain exceptions raised by API auth dependencies.

Mapped to HTTP or WebSocket error responses in route and dependency layers.
"""

from app.api.constants import Messages


class CurrentUserNotActiveException(Exception):
    """Raised when the authenticated user account is inactive or disabled."""

    def __init__(self) -> None:
        """Initialize CurrentUserNotActiveException."""

        super().__init__(Messages.USER_IS_NOT_ACTIVE)

from app.services.constants import Messages


class AuthenticationFailed(Exception):
    """Raised when login credentials are invalid or the account is disabled."""

    def __init__(self) -> None:
        """Initialize AuthenticationFailed."""

        super().__init__(Messages.AUTH_DATA_NOT_CORRECT)


class TokenCheckFailed(Exception):
    """Raised when a JWT is missing, invalid, expired, or fails Redis rotation checks."""

    def __init__(self) -> None:
        """Initialize TokenCheckFailed."""

        super().__init__(Messages.TOKEN_NOT_VALID)

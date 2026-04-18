"""
Configuration DTOs used by settings.

Holds validated config values (e.g. JWT secret and algorithm) for use in auth code.
"""

from pydantic import BaseModel


class AuthConfigDataDomain(BaseModel):
    """JWT signing and expiration parameters for token services.

    Attributes:
        access_secret_key: Symmetric key for signing and verifying access tokens.
        refresh_secret_key: Symmetric key for signing and verifying refresh tokens.
        refresh_token_entropy: Byte length fed to ``secrets.token_urlsafe`` for JWT ID values.
        algorithm: JWS algorithm name (for example ``HS256``).
        access_token_exp_time_minutes: Access token lifetime expressed in minutes.
        refresh_token_exp_time_hours: Refresh token lifetime expressed in hours.
    """

    access_secret_key: str
    refresh_secret_key: str
    refresh_token_entropy: int
    algorithm: str
    access_token_exp_time_minutes: float
    refresh_token_exp_time_hours: float

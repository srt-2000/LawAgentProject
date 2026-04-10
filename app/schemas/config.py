"""
Configuration DTOs used by settings.

Holds validated config values (e.g. JWT secret and algorithm) for use in auth code.
"""

from pydantic import BaseModel


class AuthConfigDataDomain(BaseModel):
    """JWT signing and expiration parameters for token services.

    Attributes:
        secret_key: Secret used to sign and verify tokens.
        refresh_secret_key: Secret used to sign and verify refresh tokens.
        algorithm: Algorithm name (e.g. HS256).
        access_token_exp_time_minutes: Access token lifetime in minutes.
        refresh_token_exp_time_hours: Refresh token lifetime in hours.
    """

    secret_key: str
    refresh_secret_key: str
    algorithm: str
    access_token_exp_time_minutes: float
    refresh_token_exp_time_hours: float

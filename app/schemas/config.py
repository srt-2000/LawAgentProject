"""
Configuration DTOs consumed by settings and token services.

Holds validated auth parameters passed from :class:`~app.config.AuthSettings` into
JWT helpers without re-reading the environment.
"""

from pydantic import BaseModel


class AuthConfigDataDomain(BaseModel):
    """JWT signing and lifetime parameters shared by token services.

    Attributes:
        access_secret_key: Symmetric key for signing and verifying access tokens.
        refresh_secret_key: Symmetric key for signing and verifying refresh tokens.
        refresh_token_entropy: Random byte count passed to ``secrets.token_urlsafe`` when
            minting refresh ``jti`` values.
        algorithm: JWS algorithm name (for example ``HS256``).
        access_token_exp_time_sec: Access token lifetime in whole seconds.
        refresh_token_exp_time_sec: Refresh token lifetime in whole seconds.
    """

    access_secret_key: str
    refresh_secret_key: str
    refresh_token_entropy: int
    algorithm: str
    access_token_exp_time_sec: int
    refresh_token_exp_time_sec: int

"""
Configuration DTOs used by settings.

Holds validated config values (e.g. JWT secret and algorithm) for use in auth code.
"""

from pydantic import BaseModel


class AuthConfigDTO(BaseModel):
    """JWT signing parameters passed from AuthSettings into token encode/decode.

    Attributes:
        secret_key: Secret used to sign and verify tokens.
        algorithm: Algorithm name (e.g. HS256).
    """

    secret_key: str
    algorithm: str

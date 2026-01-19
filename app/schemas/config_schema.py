"""
Configuration data transfer objects.

This module defines schemas for application configuration data.
"""

from pydantic import BaseModel


class AuthConfigDTO(BaseModel):
    """Authentication configuration data.

    Attributes:
        secret_key: JWT secret key.
        algorithm: JWT encoding algorithm.
    """

    secret_key: str
    algorithm: str

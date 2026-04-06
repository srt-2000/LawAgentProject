from pydantic import BaseModel, ConfigDict

from app.schemas.constants import FieldValues


class ResponseAccessTokenPayloadDTO(BaseModel):
    """Decoded JWT payload after verification.

    Attributes:
        sub: Subject (user ID as string).
        exp: Expiration time (Unix timestamp); None if not present.
    """

    sub: str
    exp: int | None


class RedisKeyValueDomain(BaseModel):
    model_config = ConfigDict(frozen=True, extra=FieldValues.FORBID_VALUE)

    key: str
    value_hash: str

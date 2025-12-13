from pydantic import BaseModel


class ResponsePayloadDTO(BaseModel):
    sub: str
    exp: int | None
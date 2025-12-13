from pydantic import BaseModel


class ResponseAuthDataDTO(BaseModel):
    secret_key: str
    algorithm: str
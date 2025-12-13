from pydantic import BaseModel


class WebSocketMessageDTO(BaseModel):
    message: str

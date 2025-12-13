from pydantic import ConfigDict, BaseModel


class MessageOut(BaseModel):
    id: int
    context: str
    chat_id: int
    is_bot: bool

    model_config = ConfigDict(from_attributes=True)



class ChatOut(BaseModel):
    id: int
    title: str
    user_id: int
    messages:list[MessageOut] | None = None

    model_config = ConfigDict(from_attributes=True)


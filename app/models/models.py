from enum import Enum

from sqlalchemy import Integer, String, ForeignKey, Text, BOOLEAN, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseSQLModel



class Role(Enum):
    admin = "admin"
    user = "user"


class User(BaseSQLModel):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True, nullable=False)

    chats: Mapped[list["Chat"]] = relationship(back_populates="user")

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id},"
            f"name={self.name},"
            f"role={self.role},"
            f"is_active={self.is_active}"
        )

    def __repr__(self) -> str:
        return str(self)



class Chat(BaseSQLModel):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    user: Mapped["User"] = relationship("User", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id},"
            f"title={self.title},"
            f"user_id={self.user_id}"
        )

    def __repr__(self) -> str:
        return str(self)



class Message(BaseSQLModel):

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context: Mapped[str] = mapped_column(Text)
    chat_id: Mapped[int] = mapped_column(Integer, ForeignKey("chat.id"))
    is_bot: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")

    def __str__(self) -> str:
        return (
            f"{self.__class__.__name__}(id={self.id},"
            f"context={self.context[:50]}...,"
            f"chat_id={self.chat_id},"
            f"is_it_bot_answer={self.is_bot}"
        )

    def __repr__(self) -> str:
        return str(self)

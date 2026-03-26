"""
ORM models for users, chats, and messages.

User has many Chats; Chat has many Messages. Role enum for user role.
Cascade deletes: user -> chats -> messages.
"""

from enum import Enum

from sqlalchemy import Integer, String, ForeignKey, Text, BOOLEAN, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import BaseSQLModel


class Role(Enum):
    """User role enumeration."""

    admin = "admin"
    user = "user"


class User(BaseSQLModel):
    """User model representing application users.

    Attributes:
        id: Primary key.
        name: User's display name.
        email: Unique email address.
        password_hash: Hashed password.
        role: User role (admin or user).
        is_active: Account active status.
        chats: Related chat sessions.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[Role] = mapped_column(SQLEnum(Role), default=Role.user, nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True, nullable=False)

    chats: Mapped[list["Chat"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        order_by=lambda: (Chat.created_at.asc(), Chat.id.asc())
    )

    def __str__(self) -> str:
        """String representation of the user.

        Returns:
            str: Formatted user information.
        """
        return (
            f"{self.__class__.__name__}(id={self.id},"
            f"name={self.name},"
            f"role={self.role},"
            f"is_active={self.is_active}"
        )

    def __repr__(self) -> str:
        """Detailed representation of the user.

        Returns:
            str: Same as __str__.
        """
        return str(self)


class Chat(BaseSQLModel):
    """Chat model representing conversation sessions.

    Attributes:
        id: Primary key.
        title: Optional chat title.
        user_id: Foreign key to user.
        user: Related user.
        messages: Related messages in this chat.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id", ondelete="CASCADE")
    )

    user: Mapped["User"] = relationship("User", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by=lambda: (Message.created_at.asc(), Message.id.asc())
    )

    def __str__(self) -> str:
        """String representation of the chat.

        Returns:
            str: Formatted chat information.
        """
        return (
            f"{self.__class__.__name__}(id={self.id},"
            f"title={self.title},"
            f"user_id={self.user_id}"
        )

    def __repr__(self) -> str:
        """Detailed representation of the chat.

        Returns:
            str: Same as __str__.
        """
        return str(self)


class Message(BaseSQLModel):
    """Message model representing individual chat messages.

    Attributes:
        id: Primary key.
        context: Message content.
        chat_id: Foreign key to chat.
        is_bot: Whether message is from bot.
        chat: Related chat.
    """

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    context: Mapped[str] = mapped_column(Text)
    chat_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("chat.id", ondelete="CASCADE")
    )
    is_bot: Mapped[bool] = mapped_column(BOOLEAN, nullable=False)

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")

    def __str__(self) -> str:
        """String representation of the message.

        Returns:
            str: Formatted message information with truncated content.
        """
        return (
            f"{self.__class__.__name__}(id={self.id},"
            f"context={self.context[:50]}...,"
            f"chat_id={self.chat_id},"
            f"is_it_bot_answer={self.is_bot}"
        )

    def __repr__(self) -> str:
        """Detailed representation of the message.

        Returns:
            str: Same as __str__.
        """
        return str(self)

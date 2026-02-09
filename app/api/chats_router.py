"""
Chat API router.

This module provides HTTP endpoints for listing, creating, fetching,
and deleting user chats.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import ScalarResult

from app.dao.chats_dao import ChatDAO
from app.dependencies.users_dependencies import CurrentUserDep
from app.models.models import Chat
from app.schemas.chats_schema import (
    ChatListDTO,
    ChatWithMessagesDTO,
    ChatListSideBarItemDTO,
    ChatBaseDTO,
)
from app.schemas.users_schema import ResponseMessageDTO

router = APIRouter(prefix="/user", tags=["Chats"])


@router.get("/chats", response_model=ChatListDTO)
async def get_user_chats_list(current_user: CurrentUserDep) -> ChatListDTO:
    """Return list of chats for the current user.

    Args:
        current_user: Authenticated current user.

    Returns:
        ChatListDTO: List of user's chats as sidebar items.
    """
    chats_scalar: ScalarResult[Chat] = await ChatDAO.get_user_chat_list(
        user_id=current_user.id
    )
    chats: ChatListDTO = ChatListDTO(
        chat_list=[
            ChatListSideBarItemDTO.model_validate(scalar_chat)
            for scalar_chat in chats_scalar
        ]
    )

    return chats


@router.post("/new_chat")
async def create_new_chat(current_user: CurrentUserDep) -> ChatBaseDTO:
    """Create a new chat for the current user.

    Args:
        current_user: Authenticated current user.

    Returns:
        ChatBaseDTO: Created chat data.
    """
    data_to_create_new_chat: dict[str, str | int] = {
        "title": f"new_chat of {current_user.id}",
        "user_id": current_user.id,
    }
    new_chat: Chat = await ChatDAO.add(**data_to_create_new_chat)

    return ChatBaseDTO.model_validate(new_chat)


@router.get("/chats/{chat_id}", response_model=ChatWithMessagesDTO)
async def get_chat_with_id(
    chat_id: int, current_user: CurrentUserDep
) -> ChatWithMessagesDTO:
    """Return a single chat with messages by ID for the current user.

    Args:
        chat_id: Chat ID.
        current_user: Authenticated current user.

    Returns:
        ChatWithMessagesDTO: Chat with its messages.

    Raises:
        HTTPException: 404 if chat not found or not owned by user.
    """
    chat: Chat | None = await ChatDAO.find_one_or_none_by_id(
        id=chat_id, user_id=current_user.id
    )
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return ChatWithMessagesDTO.model_validate(chat)


@router.delete("/chats/{chat_id}")
async def delete_chat_with_id(
    chat_id: int, current_user: CurrentUserDep
) -> ResponseMessageDTO:
    """Delete a chat by ID for the current user.

    Args:
        chat_id: Chat ID.
        current_user: Authenticated current user.

    Returns:
        ResponseMessageDTO: Message with count of deleted chats.
    """
    deleted_chats_count: int = await ChatDAO.delete(
        filter_by={"id": chat_id, "user_id": current_user.id}
    )
    message: dict[str, str] = {"message": f"{deleted_chats_count} chats deleted"}
    return ResponseMessageDTO.model_validate(message)

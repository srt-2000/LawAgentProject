"""
HTTP endpoints for chat CRUD: list, create, get one with messages, delete.
All require the current user; chats are scoped to that user.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import ScalarResult
from starlette import status

from app.constants import BaseConstants
from app.dao.exceptions import ObjectNotFoundException
from app.api.routers.constants import RouterFieldNames, RouterStandardMessages, FieldValues
from app.api.dependencies.dao import ChatDAODep
from app.api.dependencies.users import CurrentUserDep
from app.models.models import Chat
from app.schemas.chats import (
    ChatListDTO,
    ChatWithMessagesDTO,
    ChatListSideBarItemDTO,
    ChatWithMessagesDomain,
)
from app.schemas.users import ResponseMessageDTO
from app.services.chats import CurrentChatService

router = APIRouter(prefix="/chats", tags=[FieldValues.CHATS_TAG])


@router.get("/", response_model=ChatListDTO)
async def get_user_chats_list(
    current_user: CurrentUserDep, chat_dao: ChatDAODep
) -> ChatListDTO:
    """Return list of chats for the current user.

    Args:
        current_user: Authenticated current user.
        chat_dao: ChatDAO Dependency.

    Returns:
        ChatListDTO: List of user's chats as sidebar items.
    """
    chats_scalar: ScalarResult[Chat] = await chat_dao.get_user_chat_list(
        user_id=current_user.id
    )
    chats: ChatListDTO = ChatListDTO(
        chat_list=[
            ChatListSideBarItemDTO.model_validate(scalar_chat)
            for scalar_chat in chats_scalar
        ]
    )

    return chats


@router.post("/")
async def create(
    current_user: CurrentUserDep, chat_dao: ChatDAODep
) -> ChatWithMessagesDomain:
    """Create a new chat for the current user.
    @router.post("/new_chat")
    async def create_new_chat(current_user: CurrentUserDep) -> ChatWithMessagesDTO:
        Create a new chat for the current user. Returns the new chat with empty messages.

        Args:
            current_user: Authenticated current user,
            chat_dao: ChatDAO Dependency.

        Returns:
            ChatWithMessagesDTO: New chat (id, title, user_id, created_at, messages=[]).
    """
    chat_service: CurrentChatService = CurrentChatService(current_user.id, chat_dao)
    new_chat: ChatWithMessagesDomain = await chat_service.create_new_chat()

    return new_chat


@router.get("/{chat_id}", response_model=ChatWithMessagesDTO)
async def get_chat_by_id(
    chat_id: int, current_user: CurrentUserDep, chat_dao: ChatDAODep
) -> ChatWithMessagesDTO:
    """Return a single chat with messages by ID. Only if it belongs to the current user.

    Args:
        chat_id: Chat ID to fetch.
        current_user: Authenticated current user.
        chat_dao: ChatDAO Dependency.

    Returns:
        ChatWithMessagesDTO: Chat with messages.

    Raises:
        HTTPException: 404 if chat not found or not owned by user.
    """
    chat_service: CurrentChatService = CurrentChatService(current_user.id, chat_dao)

    try:
        chat: ChatWithMessagesDomain = await chat_service.get_chat_with_id(chat_id)
    except ObjectNotFoundException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=RouterStandardMessages.CHAT_NOT_FOUND,
        )

    return ChatWithMessagesDTO.model_validate(chat)


@router.delete("/{chat_id}")
async def delete_chat_with_id(
    chat_id: int, current_user: CurrentUserDep, chat_dao: ChatDAODep
) -> ResponseMessageDTO:
    """Delete a chat by ID for the current user.

    Args:
        chat_id: Chat ID.
        current_user: Authenticated current user.
        chat_dao: ChatDAO Dependency.

    Returns:
        ResponseMessageDTO: Message with count of deleted chats.
    """
    deleted_chats_count: int = await chat_dao.delete(
        filter_by={RouterFieldNames.ID: chat_id, BaseConstants.USER_ID: current_user.id}
    )
    message: dict[str, str] = {
        BaseConstants.MESSAGE_FIELD: f"{deleted_chats_count} {RouterStandardMessages.CHATS_DELETED}"
    }
    return ResponseMessageDTO.model_validate(message)

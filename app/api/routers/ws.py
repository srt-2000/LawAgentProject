"""
WebSocket chat endpoint.

Accepts connections at /ws/chat. Optional query param chat_id: if omitted, a new chat
is created; if present, that chat is loaded (must belong to the user). Then receives
messages and responds with a stub until RAG is connected.
"""

from loguru import logger
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dao.exceptions import ObjectNotFoundException
from app.api.routers.constants import RouterStandardMessages, RouterFieldNames
from app.api.dependencies.chats import WebsocketCurrentUserDep
from app.api.dependencies.dao import ChatDAODep, MessageDAODep
from app.schemas.chats import ChatWithMessagesDomain
from app.schemas.messages import WebSocketMessageDomain
from app.services.chats import WSConnectionManager, CurrentChatService
from app.services.constants import StandardMessages

router = APIRouter(prefix="/ws/chat")
chat_connection_manager = WSConnectionManager()


@router.websocket("")
@router.websocket("/")
async def websocket_chat(
    socket: WebSocket,
    user: WebsocketCurrentUserDep,
    chat_dao: ChatDAODep,
    message_dao: MessageDAODep,
) -> None:
    """Handle a single WebSocket: create or load chat, then loop on messages with stub reply."""
    raw_chat_id: str | None = socket.query_params.get(RouterFieldNames.CHAT_ID)
    current_chat_service: CurrentChatService = CurrentChatService(user.id, chat_dao)
    current_chat: ChatWithMessagesDomain

    if raw_chat_id:
        try:
            chat_id_to_check: int = int(raw_chat_id)
        except ValueError as error:
            logger.error(RouterStandardMessages.INVALID_CHAT, error)
            await socket.close(code=4400, reason=RouterStandardMessages.INVALID_CHAT)
            return
        else:
            try:
                current_chat_by_id: ChatWithMessagesDomain = (
                    await current_chat_service.get_chat_with_id(chat_id_to_check)
                )
            except ObjectNotFoundException:
                logger.error(RouterStandardMessages.CHAT_NOT_FOUND)
                await socket.close(
                    code=4404, reason=RouterStandardMessages.CHAT_NOT_FOUND
                )
                return

            current_chat = current_chat_by_id
    else:
        current_chat = await current_chat_service.create_new_chat()

    await chat_connection_manager.open_chat_connection(user.id, socket)

    welcome_message: WebSocketMessageDomain = WebSocketMessageDomain(
        message=RouterStandardMessages.WELCOME_MESSAGE,
        chat_id=current_chat.id,
        is_bot=True,
    )

    await chat_connection_manager.send_message(socket, welcome_message, message_dao)

    try:
        while True:
            message_to_receive: WebSocketMessageDomain = (
                await chat_connection_manager.receive_message(
                    socket, chat_id=current_chat.id, message_dao=message_dao
                )
            )
            if message_to_receive == StandardMessages.WS_ERROR_MESSAGE:
                break

            agent_message: WebSocketMessageDomain = WebSocketMessageDomain(
                message=f"{RouterStandardMessages.STUB_MESSAGE}, {message_to_receive.message}",
                chat_id=current_chat.id,
                is_bot=True,
            )
            await chat_connection_manager.send_message(
                socket, agent_message, message_dao
            )
    except WebSocketDisconnect:
        await chat_connection_manager.close_chat_connection(user.id, socket)

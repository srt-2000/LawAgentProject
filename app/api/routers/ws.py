"""
WebSocket chat endpoint.

Accepts connections at /ws/chat. Optional query param chat_id: if omitted, a new chat
is created; if present, that chat is loaded (must belong to the user). Then receives
messages and responds with a stub until RAG is connected.
"""

from loguru import logger
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dao.exceptions import ObjectNotFoundException
from app.api.constants import Fields, Messages
from app.api.dependencies.chats import WebsocketCurrentUserDep
from app.api.dependencies.dao import ChatDAODep, MessageDAODep
from app.schemas.chats import ChatWithMessagesDomain
from app.schemas.messages import (
    WebSocketMessageDomain,
    WebSocketMessageDTO,
    WSIncomingMessageDTO,
)
from app.services.chats import WSConnectionManager, CurrentChatService

router = APIRouter(prefix="/ws/chat")
chat_connection_manager = WSConnectionManager()


@router.websocket("/")
async def websocket_chat(
    socket: WebSocket,
    user: WebsocketCurrentUserDep,
    chat_dao: ChatDAODep,
    message_dao: MessageDAODep,
) -> None:
    """Handle one WebSocket chat session: resolve chat, exchange messages, stub bot reply.

    Args:
        socket: Client WebSocket connection.
        user: Authenticated user from handshake cookies.
        chat_dao: Chat DAO for create/load operations.
        message_dao: Message DAO for persisting user and bot messages.

    Optional query param ``chat_id``: if omitted, a new chat is created and a welcome
    message is sent; if present, that chat is loaded (must belong to ``user``).
    Invalid ``chat_id`` closes with code 4400; missing chat with 4404.

    Message loop: receive JSON, persist user message, build stub bot reply, persist and
    send bot message. Exits the loop on ``WS_ERROR_MESSAGE`` from receive. On disconnect,
    unregisters the connection via ``chat_connection_manager``.
    """
    raw_chat_id: str | None = socket.query_params.get(Fields.CHAT_ID)
    new_chat_created_in_ws: bool = raw_chat_id is None
    current_chat_service: CurrentChatService = CurrentChatService(user.id, chat_dao)
    current_chat: ChatWithMessagesDomain

    if raw_chat_id:
        try:
            chat_id_to_check: int = int(raw_chat_id)
        except ValueError as error:
            logger.error(Messages.INVALID_CHAT, error)
            await socket.close(code=4400, reason=Messages.INVALID_CHAT)
            return
        else:
            try:
                current_chat_by_id: ChatWithMessagesDomain = (
                    await current_chat_service.get_chat_with_id(chat_id_to_check)
                )
            except ObjectNotFoundException:
                logger.error(Messages.CHAT_NOT_FOUND)
                await socket.close(code=4404, reason=Messages.CHAT_NOT_FOUND)
                return

            current_chat = current_chat_by_id
    else:
        current_chat = await current_chat_service.create_new_chat()

    await chat_connection_manager.open_chat_connection(user.id, socket)

    if new_chat_created_in_ws:
        welcome_message: WebSocketMessageDTO = WebSocketMessageDTO(
            message=Messages.WELCOME_MESSAGE,
            chat_id=current_chat.id,
            is_bot=True,
        )

        await current_chat_service.send_json(socket, welcome_message)

    try:
        while True:
            received_message: WebSocketMessageDomain = (
                await current_chat_service.receive_json(
                    socket,
                    chat_id=current_chat.id,
                )
            )

            if received_message.message == Messages.WS_ERROR_MESSAGE:
                break

            await current_chat_service.save_message(received_message, message_dao)

            received_text: WSIncomingMessageDTO = WSIncomingMessageDTO(
                message=received_message.message
            )

            # agent answer domain creation and saving
            agent_message_domain: WebSocketMessageDomain = WebSocketMessageDomain(
                message=f"{Messages.STUB_MESSAGE}, {received_text.message}",
                chat_id=current_chat.id,
                is_bot=True,
            )
            await current_chat_service.save_message(agent_message_domain, message_dao)

            # agent answer dto creation and sending
            agent_message_dto: WebSocketMessageDTO = WebSocketMessageDTO(
                message=agent_message_domain.message,
                chat_id=current_chat.id,
                is_bot=True,
            )
            await current_chat_service.send_json(socket, agent_message_dto)

    except WebSocketDisconnect:
        await chat_connection_manager.close_chat_connection(user.id, socket)

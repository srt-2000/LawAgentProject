"""
WebSocket chat endpoint.

Accepts connections at /ws/chat. Optional query param chat_id: if omitted, a new chat
is created; if present, that chat is loaded (must belong to the user). Then receives
messages and responds with a stub until RAG is connected.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.api_constants import StandardMessages
from app.dependencies.chats_dependencies import WebsocketCurrentUserDep
from app.schemas.chats_schema import ChatWithMessagesDTO
from app.schemas.messages_schema import WebSocketMessageDTO
from app.services.chats_services import WSConnectionManager, CurrentChatService

router = APIRouter(prefix="/ws/chat")
chat_connection_manager = WSConnectionManager()


@router.websocket("")
@router.websocket("/")
async def websocket_chat(socket: WebSocket, user: WebsocketCurrentUserDep) -> None:
    """Handle a single WebSocket: create or load chat, then loop on messages with stub reply."""
    raw_chat_id: str | None = socket.query_params.get("chat_id")
    current_chat_service: CurrentChatService = CurrentChatService(user.id)

    if raw_chat_id:
        try:
            chat_id_to_check: int = int(raw_chat_id)
        except ValueError as error:
            print(f"Invalid chat_id format, error: {error}")
            await socket.close(code=4400, reason="Invalid chat_id")
            return
        else:
            current_chat: (
                ChatWithMessagesDTO | None
            ) = await current_chat_service.get_chat_with_id(chat_id_to_check)

            if current_chat is None:
                print("chat Not Found")
                await socket.close(code=4404, reason="Chat not found")
                return
    else:
        current_chat = await current_chat_service.create_new_chat()

    await chat_connection_manager.open_chat_connection(user.id, socket)

    welcome_message: WebSocketMessageDTO = WebSocketMessageDTO(
        message=StandardMessages.WELCOME_MESSAGE, chat_id=current_chat.id, is_bot=True
    )

    await chat_connection_manager.send_message(socket, welcome_message)

    try:
        while True:
            message_to_receive: WebSocketMessageDTO = (
                await chat_connection_manager.receive_message(
                    socket, chat_id=current_chat.id
                )
            )
            agent_message: WebSocketMessageDTO = WebSocketMessageDTO(
                message=f"STUB test message sent/receive {message_to_receive.message}",
                chat_id=current_chat.id,
                is_bot=True,
            )
            await chat_connection_manager.send_message(socket, agent_message)
    except WebSocketDisconnect:
        await chat_connection_manager.close_chat_connection(user.id, socket)

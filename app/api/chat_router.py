"""
WebSocket chat router.

This module handles WebSocket connections for real-time chat functionality.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dependencies.chats_dependencies import WebsocketCurrentUserDep
from app.schemas.services_schema import WebSocketMessageDTO
from app.services.chats_services import ConnectionManager
from app.config import settings

router = APIRouter(prefix="/ws/chat")
chat_manager = ConnectionManager()


@router.websocket("")
@router.websocket("/")
async def websocket_chat(connection: WebSocket, user: WebsocketCurrentUserDep) -> None:
    """Handle WebSocket chat connections.

    Args:
        connection: WebSocket connection instance.
        user: Authenticated user from WebSocket dependency.
    """
    await chat_manager.open_connection(connection, user.id)
    welcome_message: WebSocketMessageDTO = WebSocketMessageDTO(
        message=settings.WELCOME_MESSAGE
    )
    WebSocketMessageDTO.model_validate(welcome_message)
    await chat_manager.send_message(welcome_message, connection)

    try:
        while True:
            message_to_receive: dict[str, str] = await connection.receive_json()
            stub_message: WebSocketMessageDTO = WebSocketMessageDTO(
                message=message_to_receive["message"]
            )
            await chat_manager.send_message(stub_message, connection)
    except WebSocketDisconnect:
        await chat_manager.close_connection(connection, user.id)

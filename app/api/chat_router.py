from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.dependencies.chats_dependencies import WebsocketCurrentUserDep
from app.services.chats_services import ConnectionManager

router = APIRouter(prefix="/ws/chat")
chat_manager = ConnectionManager()


@router.websocket("")
@router.websocket("/")
async def websocket_chat(connection: WebSocket, user: WebsocketCurrentUserDep) -> None:

    await chat_manager.open_connection(connection, user.id)
    await chat_manager.send_message({"hello message": "can I help you?"}, connection)

    try:

        while True:
            message: dict = await connection.receive_json()
            await chat_manager.send_message(message, connection)
    except WebSocketDisconnect:
        await chat_manager.close_connection(connection, user.id)

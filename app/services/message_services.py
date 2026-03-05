"""
WebSocket message send/receive and persistence.

Sends and receives JSON messages over WebSocket and persists them to the message table.
Incoming messages are treated as user messages (is_bot=False); outgoing are set by caller.
"""

from fastapi import WebSocket

from app.dependencies.dao_dependencies import MessageDAODep
from app.schemas.messages_schema import WebSocketMessageDTO
from app.services.services_constants import ServiceMessages


class WSMessageServiceMixin:
    """Mixin for sending/receiving WebSocket messages and saving them to the database."""

    @staticmethod
    async def send_message(
            socket: WebSocket,
            message: WebSocketMessageDTO,
            message_dao: MessageDAODep
    ) -> None:
        """Send a message to the client as JSON and persist it in the database.

        Args:
            socket: WebSocket connection to send through.
            message: DTO with message text, chat_id, and is_bot. Sent as-is and saved to DB.
            message_dao: Message DAO Dependency.
        """
        try:
            serialized_message = message.model_dump()
            await socket.send_json(serialized_message)
        except Exception as error:
            print(f"Unexpected error sending message: {error}")
            return

        try:
            await message_dao.add(
                context=message.message, chat_id=message.chat_id, is_bot=message.is_bot
            )
        except Exception as error:
            print(f"Unexpected error saving the sent message into db: {error}")
            return

    @staticmethod
    async def receive_message(
            socket: WebSocket,
            chat_id: int,
            message_dao: MessageDAODep
    ) -> WebSocketMessageDTO:
        """Receive one JSON message from the client, persist it, and return a DTO.

        Expects client to send {"message": "text"}. chat_id is set server-side.
        On any failure returns a DTO with WS_ERROR_MESSAGE so the caller can show it.

        Args:
            socket: WebSocket connection to receive from.
            chat_id: Current chat ID (injected by server; not trusted from client).
            message_dao: Message DAO Dependency.

        Returns:
            WebSocketMessageDTO: Parsed message with chat_id and is_bot=False, or error DTO on failure.
        """
        error_message: WebSocketMessageDTO = WebSocketMessageDTO(
            message=ServiceMessages.WS_ERROR_MESSAGE,
            chat_id=chat_id,
            is_bot=False,
        )

        try:
            message: dict[str, str] = await socket.receive_json()
        except Exception as error:
            print(f"Unexpected error during receive message: {error}")
            return error_message

        try:
            received_text: str | None = message.get("message")
            received_message: WebSocketMessageDTO = WebSocketMessageDTO(
                message=received_text or "",
                chat_id=chat_id,
                is_bot=False,
            )
        except Exception as error:
            print(f"Cant serialize received message: {error}")
            return error_message

        try:
            await message_dao.add(
                context=received_message.message,
                chat_id=received_message.chat_id,
                is_bot=received_message.is_bot,
            )
        except Exception as error:
            print(f"Unexpected error during saving received message to db: {error}")
            return error_message

        return received_message

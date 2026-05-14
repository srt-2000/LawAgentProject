"""
WebSocket message send/receive and persistence.

Sends and receives JSON messages over WebSocket and persists them to the message table.
Incoming messages are treated as user messages (is_bot=False); outgoing are set by caller.
"""

from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from loguru import logger

from app.api.dependencies.dao import MessageDAODep
from app.schemas.messages import WebSocketMessageDomain, WebSocketMessageDTO
from app.services.constants import Messages, Fields


class WSMessageRepositoryService:
    @staticmethod
    async def save_message(
        message: WebSocketMessageDomain, message_dao: MessageDAODep
    ) -> None:
        try:
            await message_dao.add(
                context=message.message, chat_id=message.chat_id, is_bot=message.is_bot
            )
        except Exception as error:
            logger.error(f"{Messages.SAVE_MESSAGE_TO_DB_ERROR} {error}")
            return


class WSMessageService(WSMessageRepositoryService):
    """Mixin for sending/receiving WebSocket messages and saving them to the database."""

    @staticmethod
    async def send_json(socket: WebSocket, message: WebSocketMessageDTO) -> None:
        """Send a message to the client as JSON and persist it in the database."""

        try:
            serialized_message = message.model_dump()
            await socket.send_json(serialized_message)
        except WebSocketDisconnect:
            raise
        except Exception as error:
            logger.error(f"{Messages.SEND_MESSAGE_ERROR} {error}")
            return

    @staticmethod
    async def receive_json(socket: WebSocket, chat_id: int) -> WebSocketMessageDomain:
        """Receive one JSON message from the client, and return a DTO.

        Expects client to send {"message": "text"}. chat_id is set server-side.
        On any failure returns a DTO with WS_ERROR_MESSAGE so the caller can show it.

        Args:
            socket: WebSocket connection to receive from.
            chat_id: Current chat ID (injected by server; not trusted from client).

        Returns:
            WebSocketMessageDomain: Parsed message with chat_id and is_bot=False, or error DTO on failure.
        """
        error_message_domain: WebSocketMessageDomain = WebSocketMessageDomain(
            message=Messages.WS_ERROR_MESSAGE,
            chat_id=chat_id,
            is_bot=False,
        )

        try:
            message: dict[str, str] = await socket.receive_json()
        except WebSocketDisconnect:
            raise
        except Exception as error:
            logger.error(f"{Messages.RECEIVE_MESSAGE_ERROR} {error}")
            return error_message_domain

        try:
            received_text: str | None = message.get(Fields.MESSAGE)
            received_message: WebSocketMessageDomain = WebSocketMessageDomain(
                message=received_text,
                chat_id=chat_id,
                is_bot=False,
            )
        except Exception as error:
            logger.error(f"{Messages.SERIALIZE_MESSAGE_ERROR} {error}")
            return error_message_domain

        return received_message

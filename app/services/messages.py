"""
WebSocket message send/receive and persistence.

Provides JSON send/receive helpers and a repository helper that persists messages.
Incoming messages are treated as user messages (is_bot=False); outgoing ``is_bot`` is set by caller.
"""

from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from loguru import logger

from app.api.dependencies.dao import MessageDAODep
from app.schemas.messages import WebSocketMessageDomain, WebSocketMessageDTO
from app.services.constants import Messages, Fields


class WSMessageRepositoryService:
    """Persist WebSocket messages to the database."""

    @staticmethod
    async def save_message(
        message: WebSocketMessageDomain, message_dao: MessageDAODep
    ) -> None:
        """Save a message to the database.

        Args:
            message: Domain message with text, chat_id, and is_bot flag.
            message_dao: Message DAO bound to the current request session.

        Logs errors and returns without raising if persistence fails.
        """
        try:
            await message_dao.add(
                context=message.message, chat_id=message.chat_id, is_bot=message.is_bot
            )
        except Exception as error:
            logger.error(f"{Messages.SAVE_MESSAGE_TO_DB_ERROR} {error}")
            return


class WSMessageService(WSMessageRepositoryService):
    """Send and receive JSON WebSocket messages (persistence via ``save_message``)."""

    @staticmethod
    async def send_json(socket: WebSocket, message: WebSocketMessageDTO) -> None:
        """Send a message to the client as JSON.

        Args:
            socket: WebSocket connection to send on.
            message: DTO serialized with ``model_dump`` before ``send_json``.

        Raises:
            WebSocketDisconnect: Re-raised when the client disconnects during send.
        """
        try:
            serialized_message = message.model_dump()
            await socket.send_json(serialized_message)
        except WebSocketDisconnect:
            logger.warning(Messages.WS_DISCONNECTED)
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
            logger.warning(Messages.WS_DISCONNECTED)
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

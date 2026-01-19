"""
WebSocket connection management service.

This module manages WebSocket connections for chat functionality.
"""

from fastapi import WebSocket

from app.schemas.services_schema import WebSocketMessageDTO


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting.

    Attributes:
        active_connections: Map of user IDs to their active WebSocket connections.
        user_chats: Map of user IDs to their chat IDs.
    """

    def __init__(self) -> None:
        """Initialize connection manager with empty connection maps."""
        self.active_connections: dict[int, set[WebSocket]] = {}
        self.user_chats: dict[int, list[int]] = {}

    async def open_connection(self, connection: WebSocket, user_id: int) -> None:
        """Accept and register a new WebSocket connection.

        Args:
            connection: WebSocket connection to accept.
            user_id: ID of the user connecting.
        """
        await connection.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        else:
            self.active_connections[user_id].add(connection)

    async def close_connection(self, connection: WebSocket, user_id: int) -> None:
        """Close and unregister a WebSocket connection.

        Args:
            connection: WebSocket connection to close.
            user_id: ID of the user disconnecting.
        """
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(connection)

        if not self.active_connections[user_id]:
            del self.active_connections[user_id]

    @staticmethod
    async def send_message(message: WebSocketMessageDTO, connection: WebSocket) -> None:
        """Send a message through WebSocket connection with error handling.

        Args:
            message: Message DTO to send.
            connection: WebSocket connection to send through.
        """
        try:
            serialized_message = message.model_dump()
            await connection.send_json(serialized_message)
        except (ConnectionResetError, BrokenPipeError) as error:
            print(f"Client disconnected from WebSocket error {error}")
        except RuntimeError as error:
            error_msg = str(error).lower()
            if "not connected" in error_msg or "disconnect" in error_msg:
                print("WebSocket connection is closed")
            elif "send" in error_msg and "await" in error_msg:
                print("WebSocket send called in wrong state")
            else:
                print(f"WebSocket runtime error: {error}")
        except ValueError as error:
            print(f"Invalid data format for WebSocket, error: {error}")
        except Exception as error:
            print(f"Unexpected error sending message: {error}")

import asyncio
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    """Manages active WebSocket connections and handles broadcasting.

    This class maintains a list of active WebSocket connections and provides
    methods to connect, disconnect, and broadcast messages to all clients.
    """

    def __init__(self):
        """Initializes the ConnectionManager.
        
        Attributes:
            active_connections (List[WebSocket]): A list to store and manage
                active WebSocket connections.
        """
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts and registers a new WebSocket connection.

        Args:
            websocket (WebSocket): The incoming WebSocket connection to accept
                and add to the active list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes a WebSocket connection from the active list.

        Args:
            websocket (WebSocket): The WebSocket connection to remove.

        Notes:
            The removal operation is wrapped in a `try...except ValueError`
            block to safely handle potential race conditions or redundant calls. 
            If the connection has already been removed by a concurrent task, 
            `list.remove()` raises a `ValueError`, which is caught and ignored
            to prevent the application from crashing.
        """
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            pass

    async def broadcast(self, data: dict):
        """Broadcasts a JSON message to all active WebSocket connections concurrently.

        If a send operation fails, it will be ignored, 
        and the broadcast will continue to other clients.

        Args:
            data (dict): The data (serializable to JSON) to send.
        """
        tasks = [conn.send_json(data) for conn in self.active_connections]
        
        await asyncio.gather(*tasks, return_exceptions=True)

# create an instance of the class, establishes a single shared point of control for all WebSocket connection
manager = ConnectionManager()
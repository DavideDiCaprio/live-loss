from fastapi import WebSocket
from typing import List

class ConnectionManager:
    """
    Manages active WebSocket connections and handles broadcasting.
    """
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accepts and registers a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Removes a closed connection."""
        self.active_connections.remove(websocket)

    async def broadcast(self, data: dict):
        """Sends data (JSON format) to all active clients."""
        send_tasks = [conn.send_json(data) for conn in self.active_connections]
        
        for task in send_tasks:
            try:
                await task
            except Exception:
                pass

manager = ConnectionManager()
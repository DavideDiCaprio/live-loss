from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets import manager
import json 

router = APIRouter(
    tags=["Realtime"]
)

@router.websocket("/ws/realtime/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # Register the connection
    await manager.connect(websocket)
    print(f"User {user_id} connected.")

    try:
        while True:
            # Listen for incoming messages ()
            data = await websocket.receive_text()
            
            message_payload = {
                "type": "chat_message",
                "sender_id": user_id,
                "message": data
            }
            
            await manager.broadcast(message_payload)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"User {user_id} disconnected.")
        await manager.broadcast({"type": "status", "message": f"User {user_id} left."})
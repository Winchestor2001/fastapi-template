from fastapi import WebSocket, APIRouter

from app.websocket.services import WebSocketManager

from loggers import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.websocket("/")
async def websocket_endpoint(websocket: WebSocket, branch_id: str):
    manager = WebSocketManager(websocket, branch_id)

    if not await manager.accept_connection():
        return

    await manager.connect_rabbitmq()

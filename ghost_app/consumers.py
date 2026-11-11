"""
GHOST Django Channels WebSocket Consumer
Replaces the FastAPI WebSocket endpoint and ConnectionManager class.
Keeps the same broadcast logic.
"""

import json
from typing import Dict, Any, List
from channels.generic.websocket import AsyncWebsocketConsumer


class ConnectionManager:
    """Real-time WebSocket Connection Manager (mirrors original FastAPI version)."""

    def __init__(self):
        self.active_connections: List[AsyncWebsocketConsumer] = []

    async def connect(self, consumer: AsyncWebsocketConsumer):
        await consumer.accept()
        self.active_connections.append(consumer)

    def disconnect(self, consumer: AsyncWebsocketConsumer):
        if consumer in self.active_connections:
            self.active_connections.remove(consumer)

    async def broadcast(self, data: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send(text_data=json.dumps(data))
            except Exception:
                self.disconnect(connection)


# Global WebSocket manager singleton
ws_manager = ConnectionManager()


class GhostConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time GHOST event streaming."""

    async def connect(self):
        await ws_manager.connect(self)

    async def disconnect(self, close_code):
        ws_manager.disconnect(self)

    async def receive(self, text_data=None, bytes_data=None):
        # Echo or process incoming socket messages
        if text_data:
            await self.send(text_data=json.dumps({"ack": True, "received": text_data}))

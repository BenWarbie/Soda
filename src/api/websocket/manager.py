from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict
import asyncio
import json

class WebSocketManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast_trade(self, trade_data: Dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json({
                    "type": "trade_update",
                    "data": trade_data
                })
            except WebSocketDisconnect:
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

    async def broadcast_analytics(self, analytics_data: Dict):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json({
                    "type": "analytics_update",
                    "data": analytics_data
                })
            except WebSocketDisconnect:
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            await self.disconnect(connection)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import asyncio
import json
from .routes import trading, analytics
from .websocket.manager import WebSocketManager

app = FastAPI(title="Soda Trading Bot API")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trading.router)
app.include_router(analytics.router)

# WebSocket manager
manager = WebSocketManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast_trade(json.loads(data))
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "Soda Trading Bot API"}

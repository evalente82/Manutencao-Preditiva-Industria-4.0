# dashboard-service/app/main.py
from typing import List
from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
from datetime import datetime

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="API do Dashboard de Manutenção Preditiva", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

data_manager = ConnectionManager()
log_manager = ConnectionManager()
control_manager = ConnectionManager()

try:
    with open("initial_data.json", "r") as f:
        initial_data = json.load(f)
except FileNotFoundError:
    initial_data = []

def json_serializer_with_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

async def broadcast_data():
    """Busca dados do DB e envia para todos os clientes conectados a cada 3 segundos."""
    while True:
        await asyncio.sleep(3)
        db = SessionLocal()
        try:
            data = crud.get_latest_data_for_all_units(db, limit_per_unit=200)
            if data:
                # --- LINHA CORRIGIDA ---
                # 1. Converte cada objeto SQLAlchemy (item) para um schema Pydantic.
                # 2. Converte o schema Pydantic para um dicionário limpo e serializável.
                data_dict = [schemas.EngineData.model_validate(item).model_dump() for item in data]
                
                # O resto do código continua igual
                json_data = json.dumps(data_dict, default=json_serializer_with_datetime)
                await data_manager.broadcast(json_data)
        finally:
            db.close()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(broadcast_data())

@app.get("/api/data/initial")
def get_initial_data():
    return initial_data

@app.websocket("/ws/data")
async def websocket_data_endpoint(websocket: WebSocket):
    await data_manager.connect(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        data_manager.disconnect(websocket)

@app.websocket("/ws/sim_logs")
async def websocket_logs_endpoint(websocket: WebSocket):
    await log_manager.connect(websocket)
    try:
        while True:
            log_message = await websocket.receive_text()
            await log_manager.broadcast(log_message)
    except WebSocketDisconnect:
        log_manager.disconnect(websocket)

@app.websocket("/ws/sim_control")
async def websocket_control_endpoint(websocket: WebSocket):
    await control_manager.connect(websocket)
    try:
        while True:
            command = await websocket.receive_text()
            if command in ["START", "STOP"]:
                await control_manager.broadcast(command)
    except WebSocketDisconnect:
        control_manager.disconnect(websocket)
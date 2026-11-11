"""
GHOST — Personal AI Intelligence System
Main Operational Entrypoint: FastAPI Server, WebSockets & Interactive Tactical Terminal.
"""

import sys
import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from config import settings
from core.orchestrator import orchestrator
from core.mission_controller import mission_controller
from core.permission_engine import permission_engine
from core.event_bus import event_bus, GhostEvent
from devices.windows_agent import windows_agent
from devices.android_gateway import android_gateway
from agents.security_agent import security_agent
from services.task_scheduler import initialize_scheduler
from voice.text_to_speech import voice_engine

# Initialize FastAPI Command Gateway
app = FastAPI(
    title="GHOST Command Center",
    description="Central Intelligence Server for GHOST Personal AI System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


from fastapi.responses import HTMLResponse, StreamingResponse, Response
from pathlib import Path
import io
import tempfile

# Request Models
class CommandRequest(BaseModel):
    command: str
    operator_token: Optional[str] = None


class DeviceRegisterRequest(BaseModel):
    device_id: str
    name: str
    ip_address: str
    battery_percent: int = 100


class NotificationIngestRequest(BaseModel):
    device_id: str
    app_name: str
    title: str
    content: str
    priority: str = "STANDARD"


class AuthorizationRequest(BaseModel):
    token: str


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None


# Real-time WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, data: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(data)
            except Exception:
                self.disconnect(connection)


ws_manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    initialize_scheduler()
    # Hook event bus to broadcast to WebSocket clients
    async def _broadcast_events(event: GhostEvent):
        await ws_manager.broadcast({
            "event": event.event_type,
            "source": event.source,
            "timestamp": event.timestamp.isoformat(),
            "payload": event.payload
        })
    event_bus.subscribe("*", _broadcast_events)
    print("\n=======================================================")
    print("   GHOST PERSONAL AI INTELLIGENCE SYSTEM — ONLINE")
    print(f"   Security Clearance: {settings.security_level}")
    print(f"   Command Center Host: http://{settings.host}:{settings.port}")
    print("   'Mission received. Executing with precision.'")
    print("=======================================================\n")


@app.get("/health")
def health_check():
    return {"status": "OPERATIONAL", "callsign": settings.callsign}


@app.get("/", response_class=HTMLResponse)
def root():
    html_path = Path(__file__).resolve().parent / "interface" / "alpha_command.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return {"callsign": settings.callsign, "status": "OPERATIONAL"}


@app.get("/alpha", response_class=HTMLResponse)
def alpha_command_ui():
    html_path = Path(__file__).resolve().parent / "interface" / "alpha_command.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return {"status": "ALPHA_UI_NOT_FOUND"}


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_ui():
    html_path = Path(__file__).resolve().parent / "interface" / "dashboard.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return {"status": "DASHBOARD_NOT_FOUND"}


@app.get("/voice", response_class=HTMLResponse)
def voice_assistant_ui():
    html_path = Path(__file__).resolve().parent / "interface" / "voice_assistant.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return {"status": "VOICE_UI_NOT_FOUND"}


@app.get("/api/telemetry")
def get_telemetry():
    return windows_agent.get_telemetry()


@app.post("/api/command")
async def execute_command(req: CommandRequest):
    result = await orchestrator.process_command(req.command, req.operator_token)
    return result


@app.get("/api/missions")
def list_missions():
    return mission_controller.list_missions(limit=20)


@app.get("/api/missions/{mission_id}")
def get_mission_detail(mission_id: str):
    mission = mission_controller.get_mission(mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    return mission


@app.post("/api/missions/authorize")
def authorize_level3(req: AuthorizationRequest):
    if permission_engine.authorize_challenge(req.token):
        return {"success": True, "message": f"Authorization token {req.token} accepted."}
    raise HTTPException(status_code=400, detail="Invalid or expired challenge token.")


@app.post("/api/mobile/register")
def register_mobile(req: DeviceRegisterRequest):
    return android_gateway.register_device(req.device_id, req.name, req.ip_address, req.battery_percent)


@app.post("/api/mobile/notification")
async def receive_notification(req: NotificationIngestRequest):
    return await android_gateway.ingest_notification(
        req.device_id, req.app_name, req.title, req.content, req.priority
    )


@app.get("/api/security/sweep")
def run_security_sweep():
    return security_agent.run_defensive_sweep()


@app.post("/api/tts")
async def text_to_speech_endpoint(req: TTSRequest):
    """
    Generate speech audio from text and return as streamable MP3.
    The UI plays this automatically whenever GHOST responds — background voice for the Operator.
    """
    text = req.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided.")

    # Clamp length to avoid runaway synthesis
    text = text[:600]

    try:
        # Try edge-tts first (high-quality, online)
        import edge_tts, asyncio, tempfile, os
        voice_name = req.voice or settings.voice_name
        tts = edge_tts.Communicate(text, voice_name)

        # Collect audio bytes into memory
        audio_buffer = io.BytesIO()
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()

        if audio_bytes:
            return Response(
                content=audio_bytes,
                media_type="audio/mpeg",
                headers={
                    "Cache-Control": "no-cache",
                    "Content-Disposition": "inline; filename=ghost_voice.mp3",
                }
            )

    except Exception as e:
        print(f"[TTS] edge-tts failed: {e} — attempting offline fallback")

    # Offline fallback: pyttsx3 → WAV via temp file
    try:
        import pyttsx3, wave, os, tempfile
        engine = pyttsx3.init()
        engine.setProperty('rate', 165)
        engine.setProperty('volume', 0.95)

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        tmp_path = tmp.name
        tmp.close()

        engine.save_to_file(text, tmp_path)
        engine.runAndWait()

        if os.path.exists(tmp_path):
            with open(tmp_path, "rb") as f:
                wav_bytes = f.read()
            os.unlink(tmp_path)
            return Response(
                content=wav_bytes,
                media_type="audio/wav",
                headers={"Cache-Control": "no-cache"}
            )
    except Exception as e2:
        print(f"[TTS] Offline fallback also failed: {e2}")

    raise HTTPException(status_code=503, detail="TTS synthesis unavailable.")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process incoming socket messages
            await websocket.send_json({"ack": True, "received": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


async def run_interactive_cli():
    """Terminal Command Interface for GHOST."""
    print("\n[GHOST TACTICAL CONSOLE ENGAGED]")
    print("Type your directive or 'exit' to terminate session.\n")
    while True:
        try:
            command = input(f"{settings.operator_name} >> ").strip()
            if not command:
                continue
            if command.lower() in ["exit", "quit", "abort"]:
                print("Session terminated. GHOST standing by in perimeter defense.")
                break

            result = await orchestrator.process_command(command)
            print(f"\n[GHOST] {result.get('response')}\n")
            if "plan" in result:
                checklist = result["plan"].get("checklist", [])
                print("--- MISSION OBJECTIVES ---")
                for task in checklist:
                    print(f"  [x] Task {task.get('task_id')}: {task.get('action')} (Clearance Level {task.get('level')})")
                print("--------------------------\n")

        except (KeyboardInterrupt, EOFError):
            break


if __name__ == "__main__":
    if "--cli" in sys.argv:
        asyncio.run(run_interactive_cli())
    else:
        uvicorn.run("main:app", host=settings.host, port=settings.port, reload=False)


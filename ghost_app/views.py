"""
GHOST Django Views
All view functions matching the original FastAPI endpoints.
Uses JsonResponse for API endpoints, HttpResponse for HTML.
Async views use Django's async support.
"""

import json
import io
import tempfile
from pathlib import Path

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from config import settings
from core.orchestrator import orchestrator
from core.mission_controller import mission_controller
from core.permission_engine import permission_engine
from devices.windows_agent import windows_agent
from devices.android_gateway import android_gateway
from agents.security_agent import security_agent
from voice.text_to_speech import voice_engine


# ─── Page Views ───────────────────────────────────────────────────────────────

@require_GET
def root(request):
    """GET / — serves alpha_command.html"""
    html_path = Path(__file__).resolve().parent / "templates" / "interface" / "alpha_command.html"
    if html_path.exists():
        return HttpResponse(html_path.read_text(encoding="utf-8"), content_type="text/html")
    return JsonResponse({"callsign": settings.callsign, "status": "OPERATIONAL"})


@require_GET
def alpha_command_ui(request):
    """GET /alpha — serves alpha_command.html"""
    html_path = Path(__file__).resolve().parent / "templates" / "interface" / "alpha_command.html"
    if html_path.exists():
        return HttpResponse(html_path.read_text(encoding="utf-8"), content_type="text/html")
    return JsonResponse({"status": "ALPHA_UI_NOT_FOUND"})


@require_GET
def dashboard_ui(request):
    """GET /dashboard — serves dashboard.html"""
    html_path = Path(__file__).resolve().parent / "templates" / "interface" / "dashboard.html"
    if html_path.exists():
        return HttpResponse(html_path.read_text(encoding="utf-8"), content_type="text/html")
    return JsonResponse({"status": "DASHBOARD_NOT_FOUND"})


@require_GET
def voice_assistant_ui(request):
    """GET /voice — serves voice_assistant.html"""
    html_path = Path(__file__).resolve().parent / "templates" / "interface" / "voice_assistant.html"
    if html_path.exists():
        return HttpResponse(html_path.read_text(encoding="utf-8"), content_type="text/html")
    return JsonResponse({"status": "VOICE_UI_NOT_FOUND"})


# ─── API Views ────────────────────────────────────────────────────────────────

@require_GET
def health_check(request):
    """GET /health"""
    return JsonResponse({"status": "OPERATIONAL", "callsign": settings.callsign})


@require_GET
def get_telemetry(request):
    """GET /api/telemetry"""
    return JsonResponse(windows_agent.get_telemetry())


@csrf_exempt
@require_POST
async def execute_command(request):
    """POST /api/command"""
    body = json.loads(request.body)
    command = body.get("command", "")
    operator_token = body.get("operator_token", None)
    result = await orchestrator.process_command(command, operator_token)
    return JsonResponse(result)


@require_GET
def list_missions(request):
    """GET /api/missions"""
    missions = mission_controller.list_missions(limit=20)
    return JsonResponse(missions, safe=False)


@require_GET
def get_mission_detail(request, mission_id: str):
    """GET /api/missions/<mission_id>"""
    mission = mission_controller.get_mission(mission_id)
    if not mission:
        return JsonResponse({"detail": "Mission not found"}, status=404)
    return JsonResponse(mission)


@csrf_exempt
@require_POST
def authorize_level3(request):
    """POST /api/missions/authorize"""
    body = json.loads(request.body)
    token = body.get("token", "")
    if permission_engine.authorize_challenge(token):
        return JsonResponse({"success": True, "message": f"Authorization token {token} accepted."})
    return JsonResponse({"detail": "Invalid or expired challenge token."}, status=400)


@csrf_exempt
@require_POST
def register_mobile(request):
    """POST /api/mobile/register"""
    body = json.loads(request.body)
    result = android_gateway.register_device(
        body.get("device_id", ""),
        body.get("name", ""),
        body.get("ip_address", ""),
        body.get("battery_percent", 100)
    )
    return JsonResponse(result)


@csrf_exempt
@require_POST
async def receive_notification(request):
    """POST /api/mobile/notification"""
    body = json.loads(request.body)
    result = await android_gateway.ingest_notification(
        body.get("device_id", ""),
        body.get("app_name", ""),
        body.get("title", ""),
        body.get("content", ""),
        body.get("priority", "STANDARD")
    )
    return JsonResponse(result)


@require_GET
def run_security_sweep(request):
    """GET /api/security/sweep"""
    return JsonResponse(security_agent.run_defensive_sweep())


@csrf_exempt
@require_POST
async def text_to_speech_endpoint(request):
    """
    POST /api/tts
    Generate speech audio from text and return as streamable MP3.
    The UI plays this automatically whenever GHOST responds — background voice for the Operator.
    """
    body = json.loads(request.body)
    text = body.get("text", "").strip()
    if not text:
        return JsonResponse({"detail": "No text provided."}, status=400)

    # Clamp length to avoid runaway synthesis
    text = text[:600]

    try:
        # Try edge-tts first (high-quality, online)
        import edge_tts
        voice_name = body.get("voice") or settings.voice_name
        tts = edge_tts.Communicate(text, voice_name)

        # Collect audio bytes into memory
        audio_buffer = io.BytesIO()
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                audio_buffer.write(chunk["data"])

        audio_buffer.seek(0)
        audio_bytes = audio_buffer.read()

        if audio_bytes:
            response = HttpResponse(audio_bytes, content_type="audio/mpeg")
            response["Cache-Control"] = "no-cache"
            response["Content-Disposition"] = "inline; filename=ghost_voice.mp3"
            return response

    except Exception as e:
        print(f"[TTS] edge-tts failed: {e} — attempting offline fallback")

    # Offline fallback: pyttsx3 → WAV via temp file
    try:
        import pyttsx3
        import os
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
            response = HttpResponse(wav_bytes, content_type="audio/wav")
            response["Cache-Control"] = "no-cache"
            return response
    except Exception as e2:
        print(f"[TTS] Offline fallback also failed: {e2}")

    return JsonResponse({"detail": "TTS synthesis unavailable."}, status=503)

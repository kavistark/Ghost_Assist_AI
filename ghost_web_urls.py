import os
import json
import asyncio
from pathlib import Path
from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import GHOST core engine
from core.orchestrator import orchestrator
from devices.windows_agent import windows_agent
from config import settings

BASE_DIR = Path(__file__).resolve().parent
HTML_PATH = BASE_DIR / "interface" / "alpha_command.html"


def hud_view(request):
    """Serves the GHOST Alpha Command Node tactical HUD."""
    if HTML_PATH.exists():
        content = HTML_PATH.read_text(encoding="utf-8")
        return HttpResponse(content, content_type="text/html")
    return HttpResponse("<h1>GHOST — ALPHA HUD NOT FOUND</h1>", status=404)


def telemetry_view(request):
    """Returns real-time telemetry."""
    data = windows_agent.get_telemetry()
    return JsonResponse(data)


@csrf_exempt
def command_view(request):
    """Handles operator tactical commands via GHOST dual-LLM orchestrator."""
    if request.method != "POST":
        return JsonResponse({"error": "POST method required"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        command = data.get("command", "")
        token = data.get("operator_token")
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(orchestrator.process_command(command, token))
        loop.close()
        return JsonResponse(result)
    except Exception as exc:
        return JsonResponse({"status": "ERROR", "message": str(exc)}, status=500)


@csrf_exempt
def tts_view(request):
    """Synthesizes Edge-TTS audio stream."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body.decode("utf-8"))
        text = data.get("text", "")
        voice = data.get("voice", "en-US-ChristopherNeural")
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    try:
        import edge_tts
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def _synth():
            communicate = edge_tts.Communicate(text, voice)
            audio = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio += chunk["data"]
            return audio

        mp3_bytes = loop.run_until_complete(_synth())
        loop.close()
        return HttpResponse(mp3_bytes, content_type="audio/mpeg")
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)


urlpatterns = [
    path('', hud_view, name='hud'),
    path('alpha', hud_view, name='alpha'),
    path('api/telemetry', telemetry_view, name='telemetry'),
    path('api/command', command_view, name='command'),
    path('api/tts', tts_view, name='tts'),
]


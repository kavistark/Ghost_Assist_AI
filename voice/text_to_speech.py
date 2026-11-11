"""
GHOST Voice Synthesis (Text-to-Speech)
Provides military officer vocal feedback using edge-tts or local pyttsx3.
"""

import asyncio
from pathlib import Path
from typing import Optional
from config import settings

try:
    import edge_tts
except ImportError:
    edge_tts = None

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None


class VoiceEngine:
    def __init__(self, voice_name: Optional[str] = None):
        self.voice_name = voice_name or settings.voice_name
        self.output_dir = settings.log_dir / "audio"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def speak_edge(self, text: str, output_path: Optional[Path] = None) -> Optional[Path]:
        """Synthesizes high-fidelity speech via edge-tts."""
        if not edge_tts:
            return None

        out_file = output_path or (self.output_dir / "ghost_vocal.mp3")
        communicate = edge_tts.Communicate(text, self.voice_name)
        await communicate.save(str(out_file))
        return out_file

    def speak_offline(self, text: str):
        """Offline fallback using pyttsx3."""
        if not pyttsx3:
            return
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 175)
            engine.say(text)
            engine.runAndWait()
        except Exception as exc:
            print(f"[VOICE SYNTHESIS WARNING] Offline TTS failed: {exc}")


voice_engine = VoiceEngine()


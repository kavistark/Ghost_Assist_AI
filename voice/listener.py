"""
GHOST Voice Listener Service
Manages continuous background microphone monitoring, wake-word activation,
and vocal command dispatching.
"""

import asyncio
from typing import Optional, Callable
from voice.speech_to_text import stt_engine, sr
from voice.wakeword import wake_word_detector
from core.orchestrator import orchestrator
from voice.text_to_speech import voice_engine


class VoiceListener:
    def __init__(self):
        self.is_running = False
        self.microphone = sr.Microphone() if sr else None

    async def start_listening_loop(self, on_command_callback: Optional[Callable] = None):
        """Continuously monitors microphone for wake word and directives."""
        if not sr or not self.microphone or not stt_engine.recognizer:
            print("[VOICE LISTENER] Audio hardware or speech_recognition module unavailable.")
            return

        self.is_running = True
        print("[VOICE LISTENER] Audio perimeter active. Listening for 'Ghost'...")

        loop = asyncio.get_event_loop()

        while self.is_running:
            try:
                # Capture audio in thread
                audio = await loop.run_in_executor(None, self._record_audio_sample)
                if not audio:
                    continue

                transcript = await loop.run_in_executor(None, stt_engine.transcribe_audio_buffer, audio)
                if not transcript:
                    continue

                triggered, command = wake_word_detector.check_trigger(transcript)
                if triggered:
                    print(f"\n[WAKE WORD DETECTED] Order: '{command}'")
                    if command:
                        result = await orchestrator.process_command(command)
                        response_text = result.get("response", "Acknowledged.")
                        await voice_engine.speak_edge(response_text)
                    else:
                        await voice_engine.speak_edge("Ghost standing by, Sir.")

            except Exception as exc:
                print(f"[VOICE LISTENER EXCEPTION] {exc}")
                await asyncio.sleep(1)

    def _record_audio_sample(self):
        try:
            with self.microphone as source:
                stt_engine.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = stt_engine.recognizer.listen(source, timeout=3, phrase_time_limit=8)
                return audio
        except Exception:
            return None

    def stop(self):
        self.is_running = False


voice_listener = VoiceListener()


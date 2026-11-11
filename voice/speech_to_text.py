"""
GHOST Speech-to-Text (STT) Engine
Converts verbal operator input into text commands using speech_recognition.
"""

from typing import Optional

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class SpeechToTextEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer() if sr else None
        if self.recognizer:
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True

    def transcribe_audio_buffer(self, audio_data) -> Optional[str]:
        """Transcribes raw audio buffer via Google Speech API or local Sphinx."""
        if not self.recognizer:
            return None
        try:
            text = self.recognizer.recognize_google(audio_data)
            return text.strip()
        except sr.UnknownValueError:
            return None
        except Exception as exc:
            print(f"[STT WARNING] Transcription error: {exc}")
            return None


stt_engine = SpeechToTextEngine()


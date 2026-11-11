"""
GHOST Wake Word Engine
Detects voice invocation keywords (e.g., 'Ghost') to activate command listening.
"""

from typing import Tuple
from config import settings


class WakeWordDetector:
    def __init__(self, wake_word: str = "ghost"):
        self.wake_word = wake_word.lower()

    def check_trigger(self, transcript: str) -> Tuple[bool, str]:
        """
        Inspects transcript for presence of the wake word.
        Returns (is_triggered, remaining_command).
        """
        clean = transcript.lower().strip()
        if self.wake_word in clean:
            # Strip wake word and punctuation
            parts = clean.split(self.wake_word, 1)
            command = parts[1].strip(" ,.:;!?")
            return True, command
        return False, ""


wake_word_detector = WakeWordDetector(settings.wake_word)


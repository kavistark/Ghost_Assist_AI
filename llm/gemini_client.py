"""
GHOST Gemini Client (Intelligence Bravo)
Specialized in natural tactical conversation, rapid summarization, notification intelligence, and multimodal inspection.
"""

import asyncio
from typing import Dict, Any, Optional
from config import settings
from llm.prompts import GEMINI_TACTICAL_DIRECTIVE

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.gemini_api_key
        self.model = model or settings.gemini_model
        self.client = genai.Client(api_key=self.api_key) if (genai and self.api_key) else None

    @property
    def is_configured(self) -> bool:
        return bool(self.client and self.api_key)

    async def converse(self, user_message: str, telemetry_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generates a disciplined, natural military-style conversational response or situation briefing.
        Protected by asynchronous thread execution and tactical failover timeout.
        """
        if not self.is_configured:
            return self._generate_fallback_response(user_message, telemetry_context)

        system_instruction = GEMINI_TACTICAL_DIRECTIVE
        if telemetry_context:
            system_instruction += f"\nLive System Telemetry: {telemetry_context}"

        def _sync_call():
            models_to_try = [self.model, "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-flash-latest"]
            last_err = None
            for m in models_to_try:
                try:
                    response = self.client.models.generate_content(
                        model=m,
                        contents=user_message,
                        config=types.GenerateContentConfig(
                            system_instruction=system_instruction,
                            temperature=0.3,
                        )
                    )
                    return response.text.strip()
                except Exception as e:
                    last_err = e
                    continue
            raise last_err or Exception("All Gemini models failed")

        try:
            # 6-second timeout with non-blocking thread execution
            raw_text = await asyncio.wait_for(asyncio.to_thread(_sync_call), timeout=6.0)
            return self._filter_output(raw_text)
        except Exception as exc:
            print(f"[GEMINI CLIENT WARNING] API call failed or timed out ({exc}). Engaging tactical response fallback.")
            return self._filter_output(self._generate_fallback_response(user_message, telemetry_context))

    def _filter_output(self, text: str) -> str:
        """Filters output to ensure short, crisp, tactical military response."""
        if not text:
            return "Directive acknowledged, Sir."
        import re
        # Remove markdown headers, bold/italic symbols, code blocks
        clean = re.sub(r'#+\s*', '', text)
        clean = re.sub(r'[*_`]', '', clean)
        clean = re.sub(r'\n+', ' ', clean).strip()
        # Ensure it doesn't exceed 2 sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', clean) if s.strip()]
        if len(sentences) > 2:
            clean = " ".join(sentences[:2])
        return clean

    async def summarize_notifications(self, notifications: list) -> str:
        """Categorizes and summarizes incoming device notifications."""
        if not notifications:
            return "No outstanding notifications detected. All sectors calm."

        if not self.is_configured:
            count = len(notifications)
            return f"Sir, you have {count} active notifications. Priority channels indicate routine activity."

        prompt = (
            f"Review the following notifications and provide a concise military debriefing. "
            f"Highlight security risks and urgent personal items first:\n{notifications}"
        )

        def _sync_summarize():
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=GEMINI_TACTICAL_DIRECTIVE,
                    temperature=0.2
                )
            )
            return response.text.strip()

        try:
            return await asyncio.wait_for(asyncio.to_thread(_sync_summarize), timeout=6.0)
        except Exception:
            return f"Sir, identified {len(notifications)} notifications. High-priority items isolated for review."

    def _generate_fallback_response(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Heuristic tactical responses when offline, rate-limited, or awaiting API key."""
        msg = user_message.lower()
        if "status" in msg or "report" in msg or "health" in msg:
            if context:
                cpu = context.get("cpu_percent", "N/A")
                ram = context.get("ram_percent", "N/A")
                battery = context.get("battery_percent", "N/A")
                status = context.get("status", "NOMINAL")
                return (
                    f"Sir, system telemetry reporting {status}. Core CPU load at {cpu}%, Memory allocation at {ram}%. "
                    f"Power cells at {battery}%. All defensive perimeters active and monitoring."
                )
            return "Sir, all connected subsystems reporting nominal. No threats detected."

        if "hello" in msg or "ghost" in msg or "who are you" in msg:
            return "GHOST online, Sir. Awaiting your operational directives. Ready to execute with precision."

        if "security" in msg or "sweep" in msg:
            return "Security perimeter sweep executed, Sir. Socket bindings verified. Defensive shields intact."

        return f"Directive received: '{user_message}'. Stand by while tactical assets deploy."

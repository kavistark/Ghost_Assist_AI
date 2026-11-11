"""
GHOST Notification Intelligence Service
Batches, filters, and summarizes device notifications using Gemini intelligence.
"""

from typing import List, Dict, Any, Optional
from core.event_bus import event_bus, GhostEvent
from database.models import get_connection
from llm.gemini_client import GeminiClient

gemini = GeminiClient()


class NotificationService:
    def __init__(self):
        pass

    async def summarize_recent_notifications(self, limit: int = 10) -> str:
        """Retrieves recent unread notifications and generates an intelligence summary."""
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT app_name, title, content, priority, timestamp FROM notifications ORDER BY timestamp DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()

        if not rows:
            return "Sir, no outstanding notifications across connected perimeters."

        notifs = [
            {"app": r[0], "title": r[1], "content": r[2], "priority": r[3], "time": r[4]}
            for r in rows
        ]

        summary = await gemini.summarize_notifications(notifs)
        return summary


notification_service = NotificationService()


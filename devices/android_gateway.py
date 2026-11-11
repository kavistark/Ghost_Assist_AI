"""
GHOST Android Companion Gateway
Interfaces with the Android mobile agent via WebSockets & REST API.
Handles notification ingestion, device health updates, and remote command routing.
"""

from typing import Dict, Any, List
from datetime import datetime, timezone
from database.models import get_connection
from core.event_bus import event_bus, GhostEvent


class AndroidGateway:
    def __init__(self):
        self.connected_devices: Dict[str, Dict[str, Any]] = {}

    def register_device(self, device_id: str, name: str, ip_address: str, battery: int = 100) -> Dict[str, Any]:
        """Registers or updates paired Android phone status."""
        timestamp = datetime.now(timezone.utc).isoformat()
        device_info = {
            "device_id": device_id,
            "name": name,
            "device_type": "Android",
            "last_seen": timestamp,
            "status": "ONLINE",
            "ip_address": ip_address,
            "battery_percent": battery
        }
        self.connected_devices[device_id] = device_info

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO devices (device_id, name, device_type, last_seen, status, ip_address, battery_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(device_id) DO UPDATE SET
                    last_seen=excluded.last_seen,
                    status=excluded.status,
                    ip_address=excluded.ip_address,
                    battery_percent=excluded.battery_percent
                """,
                (device_id, name, "Android", timestamp, "ONLINE", ip_address, battery)
            )
            conn.commit()

        return {"success": True, "device": device_info}

    async def ingest_notification(
        self,
        device_id: str,
        app_name: str,
        title: str,
        content: str,
        priority: str = "STANDARD"
    ) -> Dict[str, Any]:
        """Receives incoming mobile notification from Android companion app."""
        timestamp = datetime.now(timezone.utc).isoformat()

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO notifications (source_device, app_name, title, content, priority, received_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (device_id, app_name, title, content, priority, timestamp)
            )
            conn.commit()

        # Broadcast via Event Bus to Notification Agent & Security Analyst
        await event_bus.publish(GhostEvent(
            event_type="NOTIFICATION_RECEIVED",
            payload={
                "source_device": device_id,
                "app": app_name,
                "title": title,
                "content": content,
                "priority": priority
            },
            source="ANDROID_GATEWAY"
        ))

        return {"success": True, "status": "INGESTED"}


# Global Android gateway instance
android_gateway = AndroidGateway()

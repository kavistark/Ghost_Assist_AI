"""
GHOST App Configuration
Initializes the scheduler and displays the GHOST startup banner on ready.
"""

from django.apps import AppConfig


class GhostAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ghost_app'
    verbose_name = 'GHOST Personal AI Intelligence System'

    def ready(self):
        from services.task_scheduler import initialize_scheduler
        from config import settings
        from core.event_bus import event_bus, GhostEvent

        initialize_scheduler()

        # Hook event bus to broadcast to WebSocket clients
        async def _broadcast_events(event: GhostEvent):
            from ghost_app.consumers import ws_manager
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

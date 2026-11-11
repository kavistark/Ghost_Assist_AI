"""
GHOST Tactical Event Bus
Provides asynchronous event routing and pub/sub capabilities across all agents and services.
"""

import asyncio
from typing import Callable, Coroutine, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class GhostEvent:
    event_type: str
    payload: Dict[str, Any]
    source: str = "SYSTEM"
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


EventHandler = Callable[[GhostEvent], Coroutine[Any, Any, None]]


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[EventHandler]] = {}
        self._wildcard_subscribers: List[EventHandler] = []
        self._lock = asyncio.Lock()

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to a specific event type or wildcard '*' for all events."""
        if event_type == "*":
            self._wildcard_subscribers.append(handler)
        else:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a subscriber from the event queue."""
        if event_type == "*":
            if handler in self._wildcard_subscribers:
                self._wildcard_subscribers.remove(handler)
        elif event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    async def publish(self, event: GhostEvent) -> None:
        """Broadcast an event to all matching handlers concurrently."""
        handlers = list(self._wildcard_subscribers)
        if event.event_type in self._subscribers:
            handlers.extend(self._subscribers[event.event_type])

        if not handlers:
            return

        tasks = [asyncio.create_task(self._safe_execute(handler, event)) for handler in handlers]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_execute(self, handler: EventHandler, event: GhostEvent) -> None:
        try:
            await handler(event)
        except Exception as exc:
            # Defensive isolation: ensure a single failing handler does not disrupt the bus
            print(f"[EVENT BUS WARNING] Handler failed for {event.event_type}: {exc}")


# Global event bus singleton
event_bus = EventBus()

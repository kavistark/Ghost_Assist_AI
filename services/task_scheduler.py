"""
GHOST Mission & Reminder Scheduler
Integrates APScheduler for delayed tasks, recurring defensive sweeps, and scheduled operations.
"""

from typing import Callable, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.event_bus import event_bus, GhostEvent

scheduler = AsyncIOScheduler()


def initialize_scheduler():
    """Starts the asynchronous tactical scheduler if not already running."""
    if not scheduler.running:
        scheduler.start()


def schedule_reminder(run_at: datetime, prompt: str, reminder_id: Optional[str] = None):
    """Schedules a one-off tactical reminder alert."""
    job_id = reminder_id or f"rem_{int(datetime.now(timezone.utc).timestamp())}"

    async def _reminder_trigger():
        print(f"\n[TACTICAL REMINDER TRIGGERED] {prompt}")
        await event_bus.publish(GhostEvent(
            event_type="REMINDER_ALERT",
            payload={"reminder_id": job_id, "prompt": prompt, "fired_at": datetime.now(timezone.utc).isoformat()},
            source="SCHEDULER"
        ))

    scheduler.add_job(_reminder_trigger, 'date', run_date=run_at, id=job_id)
    return job_id


def schedule_recurring_sweep(interval_seconds: int, job_name: str, coroutine_fn: Callable):
    """Schedules a recurring background scan or health monitor."""
    scheduler.add_job(coroutine_fn, 'interval', seconds=interval_seconds, id=job_name, replace_existing=True)

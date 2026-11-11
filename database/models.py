"""
GHOST SQLite Database Layer & Mission Models
Manages structured persistence for missions, task checklists, audit records, and paired devices.
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from config import settings


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.database_path))
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """Builds database schema for tactical missions, tasks, and telemetry."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # Missions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                mission_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                scheduled_time TEXT,
                rationale TEXT,
                assigned_agent TEXT DEFAULT 'OPERATIONS_AGENT',
                checklist_json TEXT NOT NULL,
                completion_report TEXT
            )
        """)

        # Devices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                device_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                device_type TEXT NOT NULL,
                last_seen TEXT NOT NULL,
                status TEXT NOT NULL,
                ip_address TEXT,
                battery_percent INTEGER
            )
        """)

        # Notifications Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_device TEXT NOT NULL,
                app_name TEXT NOT NULL,
                title TEXT,
                content TEXT,
                priority TEXT DEFAULT 'STANDARD',
                received_at TEXT NOT NULL,
                is_read INTEGER DEFAULT 0
            )
        """)

        conn.commit()


# Initialize on import
initialize_database()


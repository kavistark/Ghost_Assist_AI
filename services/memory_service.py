"""
GHOST Persistent Memory & Intel Dossier Service
Maintains tactical key-value directives, mission history, and operator preferences.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from database.models import get_connection


class MemoryService:
    def __init__(self):
        self._init_memory_table()

    def _init_memory_table(self):
        with get_connection() as conn:
            conn.cursor().execute("""
                CREATE TABLE IF NOT EXISTS operational_memory (
                    key TEXT PRIMARY KEY,
                    category TEXT NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def store_intel(self, key: str, value: str, category: str = "DIRECTIVE"):
        """Saves or updates a memory node."""
        with get_connection() as conn:
            conn.cursor().execute("""
                INSERT INTO operational_memory (key, category, value, updated_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    category=excluded.category,
                    updated_at=excluded.updated_at
            """, (key, category, value, datetime.now(timezone.utc).isoformat()))
            conn.commit()

    def recall_intel(self, key: str) -> Optional[str]:
        """Retrieves a specific memory node."""
        with get_connection() as conn:
            row = conn.cursor().execute("SELECT value FROM operational_memory WHERE key = ?", (key,)).fetchone()
            return row["value"] if row else None

    def list_intel(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Enumerates stored intelligence records."""
        with get_connection() as conn:
            cursor = conn.cursor()
            if category:
                rows = cursor.execute("SELECT * FROM operational_memory WHERE category = ?", (category,)).fetchall()
            else:
                rows = cursor.execute("SELECT * FROM operational_memory ORDER BY updated_at DESC").fetchall()
            return [{"key": r["key"], "category": r["category"], "value": r["value"], "updated_at": r["updated_at"]} for r in rows]


memory_service = MemoryService()


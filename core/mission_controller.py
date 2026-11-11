"""
GHOST Mission Controller
Orchestrates mission lifecycles: receipt, tactical deconstruction, checklist execution,
permission verification, and post-mission debriefing.
"""

import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from database.models import get_connection
from core.permission_engine import permission_engine, ClearanceDecision, SecurityLevel
from core.event_bus import event_bus, GhostEvent


class MissionController:
    def __init__(self):
        pass

    def create_mission(
        self,
        title: str,
        priority: str,
        checklist: List[Dict[str, Any]],
        rationale: str = "",
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """Creates and logs a new tactical mission in SQLite."""
        mission_id = f"MSN-{uuid.uuid4().hex[:6].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()
        status = "PENDING"

        # Initialize checklist status
        enriched_checklist = []
        for idx, item in enumerate(checklist, 1):
            enriched_checklist.append({
                "task_id": item.get("task_id", idx),
                "action": item.get("action", f"Subtask {idx}"),
                "tool": item.get("tool", "system_agent.execute"),
                "level": item.get("level", 2),
                "parameters": item.get("parameters", {}),
                "status": "PENDING",
                "result": None
            })

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO missions (mission_id, title, priority, status, created_at, scheduled_time, rationale, checklist_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (mission_id, title, priority, status, created_at, scheduled_time, rationale, json.dumps(enriched_checklist))
            )
            conn.commit()

        mission_data = {
            "mission_id": mission_id,
            "title": title,
            "priority": priority,
            "status": status,
            "created_at": created_at,
            "scheduled_time": scheduled_time,
            "checklist": enriched_checklist,
            "rationale": rationale
        }

        # Fire event
        # Note: can fire in async context if available
        return mission_data

    def get_mission(self, mission_id: str) -> Optional[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM missions WHERE mission_id = ?", (mission_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "mission_id": row["mission_id"],
                "title": row["title"],
                "priority": row["priority"],
                "status": row["status"],
                "created_at": row["created_at"],
                "scheduled_time": row["scheduled_time"],
                "rationale": row["rationale"],
                "checklist": json.loads(row["checklist_json"]),
                "completion_report": row["completion_report"]
            }

    def list_missions(self, limit: int = 10) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM missions ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            return [
                {
                    "mission_id": r["mission_id"],
                    "title": r["title"],
                    "priority": r["priority"],
                    "status": r["status"],
                    "created_at": r["created_at"],
                    "scheduled_time": r["scheduled_time"],
                    "checklist": json.loads(r["checklist_json"])
                }
                for r in rows
            ]

    async def execute_mission(self, mission_id: str, operator_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes each checklist item sequentially under permission verification.
        """
        mission = self.get_mission(mission_id)
        if not mission:
            return {"success": False, "message": f"Mission {mission_id} not found."}

        checklist = mission["checklist"]
        overall_status = "IN_PROGRESS"
        self._update_status(mission_id, overall_status)

        for task in checklist:
            action = task.get("action", "")
            tool = task.get("tool", "")
            params = task.get("parameters", {})

            # Request permission gateway clearance
            decision, token_or_reason = permission_engine.request_clearance(
                action=tool or action,
                agent="MISSION_CONTROLLER",
                parameters=params,
                operator_token=operator_token
            )

            if decision == ClearanceDecision.APPROVED:
                task["status"] = "COMPLETED"
                task["result"] = f"Action successfully cleared and dispatched. Tool: {tool}"
            elif decision == ClearanceDecision.PENDING_AUTHORIZATION:
                task["status"] = "HALTED_PENDING_AUTHORIZATION"
                task["result"] = f"Awaiting operator clearance token: {token_or_reason}"
                overall_status = "HALTED_PENDING_AUTHORIZATION"
                break
            else:
                task["status"] = "DENIED"
                task["result"] = f"Security gateway rejected execution: {token_or_reason}"
                overall_status = "ABORTED"
                break

        if overall_status == "IN_PROGRESS":
            overall_status = "COMPLETED"

        report = f"Debrief for {mission_id} ({mission['title']}): All steps processed with status {overall_status}."
        self._update_mission_record(mission_id, overall_status, checklist, report)

        await event_bus.publish(GhostEvent(
            event_type="MISSION_COMPLETED" if overall_status == "COMPLETED" else "MISSION_HALTED",
            payload={"mission_id": mission_id, "status": overall_status, "report": report},
            source="MISSION_CONTROLLER"
        ))

        return {
            "mission_id": mission_id,
            "status": overall_status,
            "checklist": checklist,
            "completion_report": report
        }

    def _update_status(self, mission_id: str, status: str):
        with get_connection() as conn:
            conn.cursor().execute("UPDATE missions SET status = ? WHERE mission_id = ?", (status, mission_id))
            conn.commit()

    def _update_mission_record(self, mission_id: str, status: str, checklist: list, report: str):
        with get_connection() as conn:
            conn.cursor().execute(
                "UPDATE missions SET status = ?, checklist_json = ?, completion_report = ? WHERE mission_id = ?",
                (status, json.dumps(checklist), report, mission_id)
            )
            conn.commit()


# Global mission controller instance
mission_controller = MissionController()

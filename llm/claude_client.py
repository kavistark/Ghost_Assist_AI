"""
GHOST Claude Client (Intelligence Alpha)
Specialized in complex reasoning, task breakdown, code analysis, and strategic planning.
"""

import json
import asyncio
from typing import Dict, Any, Optional
from config import settings
from llm.prompts import CLAUDE_PLANNING_DIRECTIVE

try:
    import anthropic
except ImportError:
    anthropic = None


class ClaudeClient:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.anthropic_api_key
        self.model = model or settings.claude_model
        self.client = anthropic.Anthropic(api_key=self.api_key) if (anthropic and self.api_key) else None

    @property
    def is_configured(self) -> bool:
        return bool(self.client and self.api_key)

    async def plan_mission(self, user_command: str, system_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Deconstructs a user command into an operational tactical mission plan.
        Protected by non-blocking thread execution and timeout.
        """
        if not self.is_configured:
            return self._generate_fallback_plan(user_command, system_context)

        context_str = f"\nActive Telemetry Context: {json.dumps(system_context or {})}"
        prompt = f"Operator Objective: '{user_command}'{context_str}\nProvide tactical JSON mission plan."

        def _sync_plan():
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                system=CLAUDE_PLANNING_DIRECTIVE,
                messages=[{"role": "user", "content": prompt}]
            )
            raw_text = response.content[0].text
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            return json.loads(raw_text)

        try:
            return await asyncio.wait_for(asyncio.to_thread(_sync_plan), timeout=6.0)
        except Exception as exc:
            print(f"[CLAUDE CLIENT WARNING] API call failed ({exc}). Engaging tactical heuristic fallback.")
            return self._generate_fallback_plan(user_command, system_context, str(exc))

    def _generate_fallback_plan(self, user_command: str, context: Optional[Dict[str, Any]] = None, error: str = "") -> Dict[str, Any]:
        """Local heuristic planner active when offline or pending API key."""
        cmd_lower = user_command.lower()
        priority = "STANDARD"
        if any(w in cmd_lower for w in ["urgent", "threat", "immediate", "emergency", "interview"]):
            priority = "HIGH"

        tasks = []
        task_id = 1

        if "clean" in cmd_lower or "organize" in cmd_lower or "file" in cmd_lower:
            tasks.append({
                "task_id": task_id,
                "action": "Scan workspace target directories",
                "tool": "file_tools.scan_directory",
                "level": 1,
                "parameters": {"target": "workspace"}
            })
            task_id += 1
            tasks.append({
                "task_id": task_id,
                "action": "Identify duplicate or orphaned files",
                "tool": "file_tools.find_duplicates",
                "level": 1,
                "parameters": {}
            })
            task_id += 1
            tasks.append({
                "task_id": task_id,
                "action": "Consolidate files into structured archive",
                "tool": "file_tools.organize_files",
                "level": 2,
                "parameters": {}
            })
            task_id += 1
        elif "interview" in cmd_lower or "remind" in cmd_lower or "schedule" in cmd_lower:
            tasks.append({
                "task_id": task_id,
                "action": "Schedule tactical notification timer",
                "tool": "task_scheduler.create_reminder",
                "level": 2,
                "parameters": {"prompt": user_command}
            })
            task_id += 1
            tasks.append({
                "task_id": task_id,
                "action": "Generate mission briefing notes & Q&A dossier",
                "tool": "knowledge_agent.generate_dossier",
                "level": 1,
                "parameters": {"topic": user_command}
            })
            task_id += 1
        elif "security" in cmd_lower or "scan" in cmd_lower or "process" in cmd_lower:
            tasks.append({
                "task_id": task_id,
                "action": "Collect system hardware & process telemetry",
                "tool": "system_tools.get_telemetry",
                "level": 1,
                "parameters": {}
            })
            task_id += 1
            tasks.append({
                "task_id": task_id,
                "action": "Audit active network socket bindings",
                "tool": "security_agent.audit_connections",
                "level": 1,
                "parameters": {}
            })
            task_id += 1
        else:
            tasks.append({
                "task_id": task_id,
                "action": f"Process direct tactical directive: {user_command}",
                "tool": "system_agent.execute_directive",
                "level": 2,
                "parameters": {"directive": user_command}
            })
            task_id += 1

        tasks.append({
            "task_id": task_id,
            "action": "Transmit mission completion debrief to Operator",
            "tool": "notification_tools.send_debrief",
            "level": 1,
            "parameters": {}
        })

        return {
            "mission_title": f"Mission: {user_command[:40]}",
            "priority": priority,
            "checklist": tasks,
            "rationale": "Tactical heuristic mission breakdown generated by GHOST Intelligence Core.",
            "engine": "claude-planning" if self.is_configured else "offline-tactical-planner",
            "notes": f"Fallback mode active: {error}" if error else "Nominal operational state"
        }


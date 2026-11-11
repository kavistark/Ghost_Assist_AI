"""
GHOST Security & Permission Engine
Implements the 3-Tier Security Clearance Gateway:
- LEVEL 1 (OBSERVE): Low risk read-only queries and status inspections.
- LEVEL 2 (EXECUTE): Controlled sandboxed operations (opening apps, scheduling).
- LEVEL 3 (AUTHORIZATION): High risk destructive or system operations requiring explicit confirmation.
"""

from enum import Enum
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import json
from pathlib import Path
from config import settings


class SecurityLevel(str, Enum):
    LEVEL_1_OBSERVE = "LEVEL_1_OBSERVE"
    LEVEL_2_EXECUTE = "LEVEL_2_EXECUTE"
    LEVEL_3_AUTHORIZATION = "LEVEL_3_AUTHORIZATION"


class ClearanceDecision(str, Enum):
    APPROVED = "APPROVED"
    PENDING_AUTHORIZATION = "PENDING_AUTHORIZATION"
    DENIED = "DENIED"


@dataclass
class AuditRecord:
    record_id: str
    timestamp: str
    action: str
    agent: str
    security_level: SecurityLevel
    parameters: Dict[str, Any]
    decision: ClearanceDecision
    operator_confirmed: bool = False
    justification: str = ""


class PermissionEngine:
    def __init__(self, audit_log_path: Optional[Path] = None):
        self.audit_log_path = audit_log_path or (settings.log_dir / "security_audit.jsonl")
        self._pending_authorizations: Dict[str, Dict[str, Any]] = {}

        # Known Level 3 High-Risk Operations
        self.high_risk_actions = {
            "delete_file",
            "remove_directory",
            "execute_shell",
            "terminate_critical_process",
            "modify_firewall",
            "send_external_communication",
            "reboot_system",
            "format_drive",
            "alter_credentials"
        }

        # Known Level 2 Controlled Operations
        self.controlled_actions = {
            "launch_application",
            "close_application",
            "move_file",
            "copy_file",
            "create_directory",
            "create_scheduled_mission",
            "set_reminder",
            "send_local_notification",
            "adjust_volume"
        }

    def assess_risk(self, action: str, parameters: Optional[Dict[str, Any]] = None) -> SecurityLevel:
        """Categorize incoming tool or agent actions into Security Levels."""
        action_lower = action.lower()
        if action_lower in self.high_risk_actions or "delete" in action_lower or "kill" in action_lower or "exec" in action_lower:
            return SecurityLevel.LEVEL_3_AUTHORIZATION
        elif action_lower in self.controlled_actions or "create" in action_lower or "write" in action_lower or "launch" in action_lower:
            return SecurityLevel.LEVEL_2_EXECUTE
        else:
            return SecurityLevel.LEVEL_1_OBSERVE

    def request_clearance(
        self,
        action: str,
        agent: str,
        parameters: Optional[Dict[str, Any]] = None,
        operator_token: Optional[str] = None
    ) -> Tuple[ClearanceDecision, str]:
        """
        Evaluate if an operation is authorized to execute.
        Returns: (Decision, TokenOrReason)
        """
        params = parameters or {}
        level = self.assess_risk(action, params)
        record_id = str(uuid.uuid4())[:8]

        # LEVEL 1: Instant auto-clearance
        if level == SecurityLevel.LEVEL_1_OBSERVE:
            self._log_audit(record_id, action, agent, level, params, ClearanceDecision.APPROVED, True, "Level 1 read-only automatic clearance.")
            return ClearanceDecision.APPROVED, "Auto-cleared (Level 1: Observe)"

        # LEVEL 2: Controlled sandbox clearance
        if level == SecurityLevel.LEVEL_2_EXECUTE:
            self._log_audit(record_id, action, agent, level, params, ClearanceDecision.APPROVED, True, "Level 2 controlled action granted under policy.")
            return ClearanceDecision.APPROVED, "Approved under Level 2 operational policy"

        # LEVEL 3: Explicit clearance verification
        if level == SecurityLevel.LEVEL_3_AUTHORIZATION:
            if operator_token and operator_token in self._pending_authorizations:
                pending = self._pending_authorizations.pop(operator_token)
                if pending["action"] == action:
                    self._log_audit(record_id, action, agent, level, params, ClearanceDecision.APPROVED, True, f"Operator verified token {operator_token}")
                    return ClearanceDecision.APPROVED, "Level 3 authorization confirmed by Operator."

            # Issue pending challenge
            auth_token = f"AUTH-{uuid.uuid4().hex[:6].upper()}"
            self._pending_authorizations[auth_token] = {
                "action": action,
                "agent": agent,
                "parameters": params,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            self._log_audit(
                record_id, action, agent, level, params,
                ClearanceDecision.PENDING_AUTHORIZATION, False,
                f"High-risk action requires Operator confirmation. Challenge token: {auth_token}"
            )
            return ClearanceDecision.PENDING_AUTHORIZATION, auth_token

        return ClearanceDecision.DENIED, "Access denied by security controller"

    def authorize_challenge(self, auth_token: str) -> bool:
        """Confirm a pending Level 3 operation token."""
        return auth_token in self._pending_authorizations

    def _log_audit(
        self,
        record_id: str,
        action: str,
        agent: str,
        level: SecurityLevel,
        params: Dict[str, Any],
        decision: ClearanceDecision,
        confirmed: bool,
        justification: str
    ):
        record = AuditRecord(
            record_id=record_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            action=action,
            agent=agent,
            security_level=level,
            parameters=params,
            decision=decision,
            operator_confirmed=confirmed,
            justification=justification
        )
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record.__dict__) + "\n")
        except Exception as exc:
            print(f"[SECURITY GATEWAY LOG FAILURE] Could not write audit log: {exc}")


# Global permission engine instance
permission_engine = PermissionEngine()

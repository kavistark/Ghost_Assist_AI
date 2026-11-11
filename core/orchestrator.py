"""
GHOST Central Orchestrator
The central command authority uniting Dual-LLM intelligence, permission gating,
specialized agent dispatch, and multi-device coordination.
"""

from typing import Dict, Any, Optional
from config import settings
from core.event_bus import event_bus, GhostEvent
from core.permission_engine import permission_engine, ClearanceDecision
from core.model_router import ModelRouter, ModelTarget
from core.mission_controller import mission_controller
from llm.claude_client import ClaudeClient
from llm.gemini_client import GeminiClient
from devices.windows_agent import windows_agent


class GhostOrchestrator:
    def __init__(self):
        self.claude = ClaudeClient()
        self.gemini = GeminiClient()
        self.router = ModelRouter(self.claude, self.gemini)
        self.callsign = settings.callsign
        self.operator_name = settings.operator_name

    def get_live_context(self) -> Dict[str, Any]:
        """Collects current hardware, security, and mission state."""
        telemetry = windows_agent.get_telemetry()
        recent_missions = mission_controller.list_missions(limit=3)
        return {
            "telemetry": telemetry,
            "active_missions": len([m for m in recent_missions if m["status"] == "IN_PROGRESS"]),
            "security_level": settings.security_level,
            "host": telemetry.get("hostname", "UNKNOWN")
        }

    async def process_command(self, user_command: str, operator_token: Optional[str] = None) -> Dict[str, Any]:
        """
        Primary operational entrypoint for all voice and text commands.
        Deconstructs intent, routes to optimal LLM, checks clearances, and executes.
        """
        context = self.get_live_context()

        # Fire Command Received event
        await event_bus.publish(GhostEvent(
            event_type="COMMAND_RECEIVED",
            payload={"command": user_command, "operator_token": operator_token},
            source="OPERATOR"
        ))

        # Check if user is supplying an authorization token for a pending Level 3 operation
        if operator_token or (user_command.strip().startswith("AUTH-")):
            token = operator_token or user_command.strip()
            if permission_engine.authorize_challenge(token):
                # Search missions halted on this token and resume
                return {
                    "callsign": self.callsign,
                    "response": f"Authorization code {token} confirmed, {self.operator_name}. Resuming halted operations.",
                    "status": "AUTHORIZED"
                }

        # Check if user is asking for camera, vision, or surveillance
        cmd_lower = user_command.lower()
        if any(w in cmd_lower for w in ["camera", "look at me", "who is in front", "optical", "what do you see", "take picture", "video feed"]):
            from tools.recon_tools import recon_engine
            recon_res = await recon_engine.analyze_camera_feed(user_command)
            return {
                "callsign": self.callsign,
                "response": recon_res.get("report", "Visual feed acquired."),
                "target_engine": "Gemini-Multimodal-Recon",
                "status": "SUCCESS",
                "frame": recon_res.get("frame")
            }

        # Check if user is asking for location, coordinates, or where they are
        if any(w in cmd_lower for w in ["location", "where am i", "where are we", "coordinates", "gps", "city"]):
            from tools.recon_tools import recon_engine
            geo = recon_engine.get_geospatial_telemetry()
            if geo.get("status") == "ACQUIRED":
                rep = f"Current coordinates: {geo['city']}, {geo['region']}, {geo['country']}. Latitude {geo['lat']}, Longitude {geo['lon']}. Connected via {geo['isp']}."
            else:
                rep = "Geospatial resolution unconfirmed, Sir. Active defensive proxy detected."
            return {
                "callsign": self.callsign,
                "response": rep,
                "target_engine": "Recon-Geospatial",
                "status": "SUCCESS"
            }

        # Check route
        target = self.router.determine_route(user_command)

        if target == ModelTarget.GEMINI:
            # Quick conversational / situational briefing response
            response_text = await self.gemini.converse(user_command, context["telemetry"])
            return {
                "callsign": self.callsign,
                "response": response_text,
                "target_engine": "Gemini-Bravo",
                "status": "SUCCESS"
            }

        else:
            # Strategic multi-step mission planning via Claude
            plan = await self.claude.plan_mission(user_command, context)
            mission = mission_controller.create_mission(
                title=plan.get("mission_title", f"Mission: {user_command[:30]}"),
                priority=plan.get("priority", "STANDARD"),
                checklist=plan.get("checklist", []),
                rationale=plan.get("rationale", "")
            )

            # Auto-execute Level 1 & Level 2 tasks
            execution_result = await mission_controller.execute_mission(mission["mission_id"])

            if execution_result["status"] == "HALTED_PENDING_AUTHORIZATION":
                reply = (
                    f"Mission plan formulated ({mission['mission_id']}). One or more actions require Level 3 clearance. "
                    f"Awaiting your authorization token to proceed."
                )
            else:
                reply = (
                    f"Mission received, {self.operator_name}. Plan {mission['mission_id']} engaged. "
                    f"{len(mission['checklist'])} operational objectives queued. Telemetry nominal."
                )

            return {
                "callsign": self.callsign,
                "mission_id": mission["mission_id"],
                "response": reply,
                "plan": plan,
                "execution_result": execution_result,
                "target_engine": "Claude-Alpha",
                "status": execution_result["status"]
            }


# Global orchestrator instance
orchestrator = GhostOrchestrator()


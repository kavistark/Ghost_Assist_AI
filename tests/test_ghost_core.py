"""
GHOST Core Test Suite
Validates Permission Engine, Model Router, Mission Lifecycle, and Telemetry.
"""

import pytest
import asyncio
from core.permission_engine import permission_engine, SecurityLevel, ClearanceDecision
from core.model_router import ModelRouter, ModelTarget
from core.mission_controller import mission_controller
from core.orchestrator import orchestrator
from llm.claude_client import ClaudeClient
from llm.gemini_client import GeminiClient
from tools.system_tools import get_hardware_telemetry


def test_permission_engine_levels():
    """Verify 3-tier clearance logic."""
    # Level 1: Observe
    lvl1 = permission_engine.assess_risk("get_hardware_telemetry")
    assert lvl1 == SecurityLevel.LEVEL_1_OBSERVE

    dec1, _ = permission_engine.request_clearance("get_hardware_telemetry", "TEST")
    assert dec1 == ClearanceDecision.APPROVED

    # Level 2: Controlled Execute
    lvl2 = permission_engine.assess_risk("launch_application")
    assert lvl2 == SecurityLevel.LEVEL_2_EXECUTE

    # Level 3: Authorization Required
    lvl3 = permission_engine.assess_risk("delete_file")
    assert lvl3 == SecurityLevel.LEVEL_3_AUTHORIZATION

    dec3, token = permission_engine.request_clearance("delete_file", "TEST")
    assert dec3 == ClearanceDecision.PENDING_AUTHORIZATION
    assert token.startswith("AUTH-")

    # Verify Challenge
    assert permission_engine.authorize_challenge(token) is True


def test_model_router_heuristics():
    """Verify routing matrix logic."""
    claude = ClaudeClient()
    gemini = GeminiClient()
    router = ModelRouter(claude, gemini)

    # Conversational / Status -> Gemini
    route_status = router.determine_route("Ghost, what is the system status?")
    assert route_status == ModelTarget.GEMINI

    # Complex Mission Planning -> Claude
    route_plan = router.determine_route("Ghost, organize my workspace files, identify duplicates and prepare a report.")
    assert route_plan == ModelTarget.CLAUDE


def test_hardware_telemetry():
    """Verify psutil hardware extraction."""
    telemetry = get_hardware_telemetry()
    assert "cpu_percent" in telemetry
    assert "ram_percent" in telemetry
    assert "status" in telemetry


@pytest.mark.asyncio
async def test_mission_lifecycle():
    """Verify mission creation, persistence, and automated checklist execution."""
    mission = mission_controller.create_mission(
        title="Tactical Diagnostic Scan",
        priority="HIGH",
        checklist=[
            {"action": "Check telemetry", "tool": "get_hardware_telemetry", "level": 1},
            {"action": "Stage test files", "tool": "create_directory", "level": 2}
        ],
        rationale="Automated test verification."
    )

    assert mission["mission_id"].startswith("MSN-")
    exec_result = await mission_controller.execute_mission(mission["mission_id"])
    assert exec_result["status"] == "COMPLETED"
    assert len(exec_result["checklist"]) == 2


@pytest.mark.asyncio
async def test_orchestrator_directive():
    """Verify orchestrator end-to-end command flow."""
    res = await orchestrator.process_command("Report status")
    assert res["status"] == "SUCCESS"
    assert "response" in res


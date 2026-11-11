"""
GHOST Cognitive Model Router
Directs tasks to either Intelligence Alpha (Claude) or Intelligence Bravo (Gemini)
based on operational complexity, latency requirements, and mission profile.
"""

from enum import Enum
from typing import Dict, Any, Tuple
from llm.claude_client import ClaudeClient
from llm.gemini_client import GeminiClient


class ModelTarget(str, Enum):
    CLAUDE = "CLAUDE_INTELLIGENCE_A"
    GEMINI = "GEMINI_INTELLIGENCE_B"
    DUAL_CONSENSUS = "DUAL_CONSENSUS"


class ModelRouter:
    def __init__(self, claude: ClaudeClient, gemini: GeminiClient):
        self.claude = claude
        self.gemini = gemini

        # Intent triggers for Intelligence Alpha (Claude)
        self.claude_triggers = {
            "plan", "mission", "organize", "analyze", "duplicate",
            "refactor", "code", "execute", "schedule", "interview",
            "workflow", "step-by-step", "breakdown", "dependencies"
        }

        # Intent triggers for Intelligence Bravo (Gemini)
        self.gemini_triggers = {
            "status", "report", "brief", "summarize", "notification",
            "hello", "who", "read", "explain", "screen", "inspect",
            "battery", "weather", "translate", "audio", "voice"
        }

    def determine_route(self, prompt: str, is_multimodal: bool = False, requires_dual_audit: bool = False) -> ModelTarget:
        """Determines the optimal intelligence model for a given directive."""
        if requires_dual_audit:
            return ModelTarget.DUAL_CONSENSUS

        if is_multimodal:
            return ModelTarget.GEMINI

        prompt_words = set(prompt.lower().split())

        claude_score = len(prompt_words.intersection(self.claude_triggers))
        gemini_score = len(prompt_words.intersection(self.gemini_triggers))

        # Check for multi-clause complexity (e.g. "and", "then", "also", "prepare")
        if any(connector in prompt.lower() for connector in ["then", "also", "prepare", "after that", "organize"]):
            claude_score += 2

        if claude_score > gemini_score:
            return ModelTarget.CLAUDE
        elif gemini_score > claude_score:
            return ModelTarget.GEMINI
        else:
            # Default to Gemini for rapid response if short/conversational, Claude if lengthy
            return ModelTarget.CLAUDE if len(prompt.split()) > 10 else ModelTarget.GEMINI

    async def route_and_execute(
        self,
        prompt: str,
        context: Dict[str, Any],
        is_multimodal: bool = False,
        requires_dual_audit: bool = False
    ) -> Tuple[ModelTarget, Any]:
        """Routes prompt to designated model and returns result."""
        target = self.determine_route(prompt, is_multimodal, requires_dual_audit)

        if target == ModelTarget.CLAUDE:
            result = await self.claude.plan_mission(prompt, context)
            return target, result

        elif target == ModelTarget.GEMINI:
            result = await self.gemini.converse(prompt, context)
            return target, result

        else:
            # Dual consensus mode: Claude creates execution plan, Gemini validates and summarizes for operator
            plan = await self.claude.plan_mission(prompt, context)
            debrief = await self.gemini.converse(
                f"Review this mission plan and provide an executive summary: {plan.get('mission_title')}",
                {"plan": plan}
            )
            return target, {"plan": plan, "debrief": debrief}


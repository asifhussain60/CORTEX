"""
Phase 20.2 Component: OrchestratorVisibility Orchestrator

Training wheels visibility system for orchestrator activity.
Provides toggleable feedback for engineers learning CORTEX.
"""

import os
from typing import Any, Dict, List, Optional


class OrchestratorVisibility:
    """
    Orchestrator visibility system - training wheels for CORTEX learning.

    Provides rich visual feedback about orchestrator engagement, stage progress,
    and intelligence activation. Designed to be disabled once engineers gain
    confidence (training wheels removed).

    Configuration:
        CORTEX_ORCHESTRATOR_VISIBILITY environment variable:
            - 'full': Show all indicators (learning phase)
            - 'failures': Show only failures (transitioning)
            - 'off': Disabled (mature phase)
    """

    def __init__(self):
        """Initialize OrchestratorVisibility."""
        pass
        self._header_cache: Dict[str, str] = {}

    def get_name(self) -> str:
        """Return orchestrator name."""
        return "OrchestratorVisibility"

    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate visibility header for orchestrator.

        Args:
            request: Dict containing:
                - orchestrator: Orchestrator name
                - stage: Current stage number
                - total_stages: Total stages
                - intelligence: List of intelligence types
                - failed: Optional failure indicator

        Returns:
            Dict containing:
                - visible: Whether to show visibility
                - header: Formatted header string
        """
        orchestrator_name = request.get("orchestrator", "Unknown")
        stage = request.get("stage", 1)
        total_stages = request.get("total_stages", 4)
        intelligence = request.get("intelligence", [])
        failed = request.get("failed", False)

        # Check if visibility should be shown
        if not should_show_visibility(failed):
            return {
                "visible": False,
                "header": ""
            }

        # Generate header
        header = self.generate_visibility_header(
            orchestrator_name,
            stage,
            total_stages,
            intelligence,
            failed
        )

        return {
            "visible": True,
            "header": header
        }

    def generate_visibility_header(
        self,
        orchestrator_name: str,
        stage: int,
        total_stages: int,
        intelligence: List[str],
        failed: bool = False
    ) -> str:
        """
        Generate formatted visibility header.

        Args:
            orchestrator_name: Name of orchestrator
            stage: Current stage
            total_stages: Total stages
            intelligence: Intelligence types engaged
            failed: Whether operation failed

        Returns:
            Formatted header string
        """
        # Check cache
        cache_key = f"{orchestrator_name}:{stage}:{total_stages}:{','.join(intelligence)}:{failed}"
        if cache_key in self._header_cache:
            return self._header_cache[cache_key]

        # Generate components
        badge = generate_badge(orchestrator_name)
        progress = generate_stage_progress(stage, total_stages, failed)
        intel_badge = generate_intelligence_badge(intelligence)

        # Assemble header
        header = f"{badge} {orchestrator_name} {progress}"
        if intel_badge:
            header += f" {intel_badge}"

        # Cache and return
        self._header_cache[cache_key] = header
        return header

    def health_check(self) -> bool:
        """Check orchestrator health."""
        return True


def generate_badge(orchestrator_name: str) -> str:
    """
    Generate badge for orchestrator type.

    Args:
        orchestrator_name: Name of orchestrator

    Returns:
        Badge emoji/text
    """
    badges = {
        "TDDOrchestrator": "🧪",
        "RefactoringOrchestrator": "♻️",
        "MasterOrchestrator": "🧠",
        "IntentRouter": "🎯",
        "EnforcementOrchestrator": "🛡️",
        "EducationalOrchestrator": "🎓",
        "ChallengeEngine": "⚔️",
        "LENSSynthesis": "🔬"
    }
    return badges.get(orchestrator_name, "⚙️")


def generate_stage_progress(
    stage: int,
    total: int,
    failed: bool = False
) -> str:
    """
    Generate stage progress dots.

    Args:
        stage: Current stage (1-indexed)
        total: Total stages
        failed: Whether operation failed

    Returns:
        Progress string (e.g., "●●○○" or "●●✗○")
    """
    if failed:
        # Show failure at current stage
        progress = "●" * (stage - 1) + "✗" + "○" * (total - stage)
    else:
        # Normal progress
        progress = "●" * stage + "○" * (total - stage)

    return progress


def generate_intelligence_badge(intelligence: List[str]) -> str:
    """
    Generate intelligence engagement badge.

    Args:
        intelligence: List of intelligence types (e.g., ["lens", "knowledge"])

    Returns:
        Intelligence badge string
    """
    if not intelligence:
        return ""

    badges = []
    if "lens" in intelligence:
        badges.append("🧠")
    if "knowledge" in intelligence:
        badges.append("📚")
    if "synthesis" in intelligence:
        badges.append("🔗")

    return " ".join(badges) if badges else ""


def should_show_visibility(failed: bool = False) -> bool:
    """
    Check if visibility should be shown based on configuration.

    Args:
        failed: Whether operation failed

    Returns:
        True if visibility should be shown
    """
    mode = os.environ.get("CORTEX_ORCHESTRATOR_VISIBILITY", "full").lower()

    if mode == "off":
        return False
    elif mode == "failures":
        return failed
    else:  # "full" or default
        return True


def health_check() -> Dict[str, Any]:
    """
    Health check for OrchestratorVisibility.

    Returns:
        Health status dict
    """
    return {
        "status": "healthy",
        "mode": os.environ.get("CORTEX_ORCHESTRATOR_VISIBILITY", "full"),
        "available": True
    }

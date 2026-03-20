"""SkillBridge adapter for orchestrator-to-skill handoff."""

from __future__ import annotations

from typing import Any, Dict, Optional

from cortex.core.registry.skill_executor import SkillExecutor


class SkillBridge:
    """Bridge for invoking skills through SkillExecutor."""

    def __init__(self, executor: Optional[SkillExecutor] = None) -> None:
        """Initialize bridge.

        Args:
            executor: Optional pre-configured skill executor.
        """
        self._executor = executor if executor is not None else SkillExecutor()

    @property
    def executor(self) -> SkillExecutor:
        """Return underlying executor."""
        return self._executor

    def invoke(self, skill_name: str, payload: Dict[str, Any]) -> Any:
        """Invoke a skill by name.

        Args:
            skill_name: Skill to execute.
            payload: Input payload.

        Returns:
            Skill result.
        """
        return self._executor.execute_skill(skill_name, payload)

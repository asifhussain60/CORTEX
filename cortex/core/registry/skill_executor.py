"""SkillExecutor runtime for M21 bridge integration.

Provides a lightweight in-process skill registry and execution contract.
"""

from __future__ import annotations

from typing import Any, Callable, Dict


class SkillExecutor:
    """Execute registered skills by name.

    Skills are callables taking a payload dictionary and returning any value.
    """

    def __init__(self) -> None:
        """Initialize an empty skill registry."""
        self._skills: Dict[str, Callable[[Dict[str, Any]], Any]] = {}

    def register_skill(self, skill_name: str, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Register a skill handler.

        Args:
            skill_name: Canonical skill name.
            handler: Callable skill implementation.
        """
        self._skills[skill_name] = handler

    def execute_skill(self, skill_name: str, payload: Dict[str, Any]) -> Any:
        """Execute a registered skill.

        Args:
            skill_name: Registered skill name.
            payload: Skill input payload.

        Returns:
            Result returned by the skill handler.

        Raises:
            KeyError: If skill name is not registered.
        """
        if skill_name not in self._skills:
            raise KeyError(f"Unknown skill: {skill_name}")
        return self._skills[skill_name](payload)

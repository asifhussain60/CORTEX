"""
Execution Coordinator - TDD workflow orchestration

AC-PHASE-24: Master Orchestrator Decomposition
- Orchestrates RED → GREEN → REFACTOR cycle
- Manages execution mode selection
- Coordinates with TDD orchestrator
"""

from __future__ import annotations

from typing import Dict, Any
from enum import Enum


class TDDPhase(Enum):
    """TDD execution phases."""
    RED = "red"
    GREEN = "green"
    REFACTOR = "refactor"


class ExecutionCoordinator:
    """
    Coordinates TDD workflow execution.

    Responsibilities:
    - Manage TDD phases
    - Execute mode selection
    - Approval gate management
    - Coordinate with TDD orchestrator

    Example:
        coordinator = ExecutionCoordinator()
        result = coordinator.execute_tdd_cycle(
            intent="IMPLEMENT",
            context={}
        )
    """

    def __init__(self):
        """Initialize execution coordinator."""
        self.tdd_orchestrator = None
        self.mode_selector = None

    def execute_tdd_cycle(
        self,
        intent: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute complete TDD cycle.

        Args:
            intent: Intent type (IMPLEMENT, FIX, etc.)
            context: Operation context

        Returns:
            TDD execution results
        """
        phases = []

        # RED phase: Test spec
        red_result = self._execute_phase(TDDPhase.RED, context)
        phases.append(red_result)

        # GREEN phase: Implementation
        green_result = self._execute_phase(TDDPhase.GREEN, context)
        phases.append(green_result)

        # REFACTOR phase: Cleanup
        refactor_result = self._execute_phase(TDDPhase.REFACTOR, context)
        phases.append(refactor_result)

        return {
            "phases": phases,
            "success": all(p.get("success") for p in phases),
            "context": context
        }

    def _execute_phase(
        self,
        phase: TDDPhase,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a single TDD phase."""
        # Delegated to TDD orchestrator
        if not self.tdd_orchestrator:
            return {
                "phase": phase.value,
                "success": False,
                "error": "TDD orchestrator not set"
            }

        try:
            result = self.tdd_orchestrator.execute_phase(phase, context)
            return {
                "phase": phase.value,
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "phase": phase.value,
                "success": False,
                "error": str(e)
            }

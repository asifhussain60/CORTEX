"""
CORTEX Phase Executors Module

Provides centralized phase execution framework following:
- CORE-038: File placement policy (proper module location)
- CORE-028: Kebab-case naming conventions
- CORE-049: Silent autonomous execution protocol
- MCP-FIRST: All operations expose via MCP tools

Architecture:
- phase_executor_factory: Creates phase executors dynamically
- phase_executor_base: Base class for all executors
- phase_orchestrator: Coordinates multi-phase execution

Authority: Phase 80 - Phase Execution Automation
"""

__version__ = "1.0.0"
__author__ = "CORTEX Architect"

from cortex.phase_executors.phase_executor_base import PhaseExecutorBase
from cortex.phase_executors.phase_executor_factory import PhaseExecutorFactory
from cortex.phase_executors.phase_orchestrator import PhaseOrchestrator

__all__ = [
    "PhaseExecutorBase",
    "PhaseExecutorFactory",
    "PhaseOrchestrator",
]

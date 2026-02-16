"""Health Orchestrator - Proactive Repository Health Management

The Health Orchestrator coordinates specialized health agents to detect and fix
code quality issues, duplications, configuration drift, and technical debt.

Architecture:
- HealthOrchestrator: Main coordinator
- Agents: Specialized detectors (duplicates, stubs, paths, tests, etc.)
- Reports: Health metrics and dashboards
- Hooks: Pre-commit/pre-push/CI integration

Author: CORTEX Framework
Phase: PHASE-92
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (no duplicates)
"""

from .health_orchestrator import HealthOrchestrator
from .agents.base_agent import BaseHealthAgent, HealthIssue, HealthCheckResult
from .reports.health_report import HealthReport, HealthMetrics

__all__ = [
    "HealthOrchestrator",
    "BaseHealthAgent",
    "HealthIssue",
    "HealthCheckResult",
    "HealthReport",
    "HealthMetrics",
]

__version__ = "1.0.0"

"""
Orchestration modules for CORTEX.

High-level orchestrators that coordinate multiple operations:
- MaintenanceOrchestratorV3: Comprehensive system maintenance workflow
- CleanupOrchestrator: File organization and cleanup workflow
- VacuumOrchestrator: Deep codebase cleanup with AST intelligence
- RefactorCycleOrchestrator: Automatic code cleanup and quality enforcement
- DocumentHygieneOrchestrator: Automatic Markdown maintenance and organization
- PlanningOrchestrator: Planning System 3.1 with temporary plan support
- TemporaryPlanManager: Implicit planning workflow management

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

from .maintenance_orchestrator_v3 import MaintenanceOrchestratorV3
from .cleanup_orchestrator import CleanupOrchestrator
from .vacuum_orchestrator import VacuumOrchestrator
from .refactor_cycle_orchestrator import RefactorCycleOrchestrator
from .document_hygiene_orchestrator import DocumentHygieneOrchestrator
from .planning_orchestrator import PlanningOrchestrator
from .temporary_plan_manager import TemporaryPlanManager

__all__ = [
    'MaintenanceOrchestratorV3',
    'CleanupOrchestrator',
    'VacuumOrchestrator',
    'RefactorCycleOrchestrator',
    'DocumentHygieneOrchestrator',
    'PlanningOrchestrator',
    'TemporaryPlanManager',
]

"""
Vacuum Orchestrator Package

Autonomous file/folder management for CORTEX.
"""

from .vacuum_orchestrator_v3 import (
    VacuumOrchestratorV3,
    VacuumConfig,
    VacuumOperation
)
from .child_spawner import (
    ChildOrchestratorSpawner,
    ChildOrchestrator,
    OrchestratorTask,
    TaskResult,
    WorkerPool
)

__all__ = [
    'VacuumOrchestratorV3',
    'VacuumConfig',
    'VacuumOperation',
    'ChildOrchestratorSpawner',
    'ChildOrchestrator',
    'OrchestratorTask',
    'TaskResult',
    'WorkerPool'
]

__version__ = '3.0.0'

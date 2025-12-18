"""
Execution Orchestrator Module

Provides workflow execution coordination with dependency blocking and
multi-orchestrator routing.

Components:
- ExecutionOrchestrator: Main orchestrator for workflow coordination
- PhaseExecution: Phase tracking dataclass
- ExecutionPlan: Complete execution plan dataclass
- ExecutionStatus: Phase status enum
- OrchestratorType: Available orchestrator types enum

Usage:
    from src.orchestrators.execution import ExecutionOrchestrator, create_execution_orchestrator
    
    orchestrator = create_execution_orchestrator(config=config, container=container)
    result = orchestrator.execute({'execution_plan': plan_data})

Author: Asif Hussain
Version: 4.0.0
"""

from .execution_orchestrator import (
    ExecutionOrchestrator,
    ExecutionStatus,
    OrchestratorType,
    PhaseExecution,
    ExecutionPlan,
    create_execution_orchestrator
)

__all__ = [
    'ExecutionOrchestrator',
    'ExecutionStatus',
    'OrchestratorType',
    'PhaseExecution',
    'ExecutionPlan',
    'create_execution_orchestrator'
]

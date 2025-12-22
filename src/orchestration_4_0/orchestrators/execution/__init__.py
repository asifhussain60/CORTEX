"""
Execution Orchestrator Package - Phase 5 Enhanced

Components:
- ExecutionOrchestrator: Main orchestrator with Phase 5 enhancements
- Schemas: Pydantic models for type-safe results
- ContextValidator: Pre-execution context validation
- ExecutionSafetyGuardrail: Safety checks and risk assessment
- SequentialChatExecutor: Sequential pipeline execution
- ParallelGroupChatExecutor: Parallel execution with synthesis
- NestedChatExecutor: Hierarchical team execution

Version: 2.0 (Post-Phase 5)
Agentic Alignment: 23% → 95%
"""

from .execution_orchestrator import ExecutionOrchestrator
from .schemas import (
    ExecutionResult, PhaseResult, PhaseStatus,
    ExecutionMode, ContextValidation, Risk, RiskSeverity, SafetyCheck
)
from .context_validator import ContextValidator
from .execution_safety_guardrail import ExecutionSafetyGuardrail
from .sequential_chat_executor import SequentialChatExecutor
from .parallel_group_chat_executor import ParallelGroupChatExecutor
from .nested_chat_executor import NestedChatExecutor

__all__ = [
    'ExecutionOrchestrator',
    'ExecutionResult',
    'PhaseResult',
    'PhaseStatus',
    'ExecutionMode',
    'ContextValidation',
    'Risk',
    'RiskSeverity',
    'SafetyCheck',
    'ContextValidator',
    'ExecutionSafetyGuardrail',
    'SequentialChatExecutor',
    'ParallelGroupChatExecutor',
    'NestedChatExecutor',
]

__version__ = '2.0'
__agentic_alignment__ = '95%'


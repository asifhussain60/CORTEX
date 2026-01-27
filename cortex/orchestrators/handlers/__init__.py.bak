"""
Master Orchestrator Handler Classes - AC-REM-HIGH-001 Refactoring

Extracts responsibility from MasterOrchestrator (1778 lines) into
specialized handler classes following Single Responsibility Principle.

Handler Classes:
- IntentClassificationHandler: Classify incoming intent
- RoutingHandler: Route to domain orchestrators
- GovernanceHandler: Validate governance compliance
- KnowledgeHandler: Query knowledge repository
- ExecutionCoordinator: Coordinate execution
- ErrorRecoveryHandler: Handle errors and recovery
"""

from cortex.orchestrators.handlers.intent_classification_handler import (
    IntentClassificationHandler,
)
from cortex.orchestrators.handlers.routing_handler import (
    RoutingHandler,
)
from cortex.orchestrators.handlers.governance_handler import (
    GovernanceHandler,
)
from cortex.orchestrators.handlers.knowledge_handler import (
    KnowledgeHandler,
)
from cortex.orchestrators.handlers.execution_coordinator import (
    ExecutionCoordinator,
)
from cortex.orchestrators.handlers.error_recovery_handler import (
    ErrorRecoveryHandler,
)

__all__ = [
    "IntentClassificationHandler",
    "RoutingHandler",
    "GovernanceHandler",
    "KnowledgeHandler",
    "ExecutionCoordinator",
    "ErrorRecoveryHandler",
]

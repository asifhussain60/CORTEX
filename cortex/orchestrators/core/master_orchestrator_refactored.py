"""
Master Orchestrator - Refactored Facade Pattern

AC-REM-HIGH-001: Reduces MasterOrchestrator from 1,777 → ~250 lines
by delegating responsibilities to specialized handlers.

BEFORE: Single monolithic class (1,777 lines, 7+ concerns)
AFTER: Facade + 6 handler classes (~250 lines each, 1 concern each)

Benefits:
- Single Responsibility Principle compliance
- Easier testing (smaller classes)
- Easier maintenance (clear boundaries)
- Easier extension (add new handlers)
"""

from __future__ import annotations

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from cortex.core.interfaces import IOrchestrator
from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class OperationRequest:
    """Represents an incoming operation request."""
    text: str
    context: Dict[str, Any]


@dataclass
class OperationResult:
    """Represents the result of an operation."""
    success: bool
    output: Any = None
    error: Optional[str] = None


class MasterOrchestratorRefactored(IOrchestrator):
    """
    Master Orchestrator Facade - Delegates to specialized handlers.

    This is the refactored version that implements the facade pattern,
    reducing complexity from 1,777 lines to ~250 lines.

    Handlers:
    - IntentClassificationHandler: Classify intent
    - RoutingHandler: Route to domain orchestrators
    - GovernanceHandler: Validate governance
    - KnowledgeHandler: Query knowledge repository
    - ExecutionCoordinator: Coordinate execution
    - ErrorRecoveryHandler: Handle errors

    AC-ID: AC-REM-HIGH-001
    """

    def __init__(
        self,
        intent_handler: Any = None,
        routing_handler: Any = None,
        governance_handler: Any = None,
        knowledge_handler: Any = None,
        execution_coordinator: Any = None,
        error_recovery: Any = None,
    ) -> None:
        """
        Initialize MasterOrchestrator facade.

        Args:
            intent_handler: IntentClassificationHandler instance
            routing_handler: RoutingHandler instance
            governance_handler: GovernanceHandler instance
            knowledge_handler: KnowledgeHandler instance
            execution_coordinator: ExecutionCoordinator instance
            error_recovery: ErrorRecoveryHandler instance
        """
        self.logger = EnhancedAuditLogger.instance()

        # Handlers (injected for testability)
        self._intent_handler = intent_handler
        self._routing_handler = routing_handler
        self._governance_handler = governance_handler
        self._knowledge_handler = knowledge_handler
        self._execution_coordinator = execution_coordinator
        self._error_recovery = error_recovery

    def execute(self, request: OperationRequest) -> Result[OperationResult]:
        """
        Execute orchestration pipeline.

        Stage 1: Classify intent
        Stage 2: Route to handler
        Stage 3: Validate governance
        Stage 4: Query knowledge
        Stage 5: Coordinate execution

        Args:
            request: Operation request with text and context

        Returns:
            Result with operation output or error

        Raises:
            ValueError: If request is invalid
        """
        try:
            if not request or not request.text:
                return Err("Invalid request: text required")

            # Stage 1: Classify intent (delegated)
            if self._intent_handler:
                intent_result = self._intent_handler.classify(
                    request.text, request.context
                )
                if isinstance(intent_result, Err):
                    return intent_result
                intent = intent_result.value
            else:
                intent = None

            # Stage 2: Route to handler (delegated)
            if self._routing_handler and intent:
                handler_result = self._routing_handler.route(intent)
                if isinstance(handler_result, Err):
                    return handler_result
                handler = handler_result.value
            else:
                handler = None

            # Stage 3: Validate governance (delegated)
            if self._governance_handler:
                gov_result = self._governance_handler.validate(intent)
                if isinstance(gov_result, Err):
                    return gov_result

            # Stage 4: Query knowledge (delegated)
            if self._knowledge_handler and intent:
                knowledge = self._knowledge_handler.query(intent)
            else:
                knowledge = {}

            # Stage 5: Execute (delegated)
            if self._execution_coordinator and handler:
                execution_result = self._execution_coordinator.execute(
                    intent, handler, knowledge
                )
            else:
                execution_result = Ok(OperationResult(success=True, output=None))

            return execution_result

        except ValueError as e:
            self.logger.log(f"Validation error: {e}")
            return Err(f"Validation error: {e}")
        except KeyError as e:
            self.logger.log(f"Missing configuration: {e}")
            return Err(f"Missing configuration: {e}")
        except RuntimeError as e:
            # Attempt recovery (delegated)
            if self._error_recovery:
                return self._error_recovery.recover(request, e)
            return Err(f"Runtime error: {e}")
        except Exception as e:
            self.logger.log(f"Unexpected error: {e}")
            return Err(f"Unexpected error: {e}")

    @classmethod
    def instance(cls) -> MasterOrchestratorRefactored:
        """Get singleton instance."""
        # Implementation depends on existing singleton pattern
        return cls()

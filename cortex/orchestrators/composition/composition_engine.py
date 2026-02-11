"""
Orchestrator Composition Engine - AR-017-02

DEPRECATED: Use cortex.orchestrators.support.composed_orchestrator instead.
This module contains composition patterns that have been superseded by the
canonical ComposedOrchestrator in support/composed_orchestrator.py.

Composition patterns for orchestrator workflows:
- Sequential: Steps executed in order
- Parallel: Steps executed concurrently
- Conditional: Steps executed based on conditions
- Delegating: Operations delegated to child orchestrators

Author: Asif Hussain
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class CompositionPattern(Enum):
    """Composition pattern enumeration"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    DELEGATING = "delegating"

    @property
    def description(self) -> str:
        """Get pattern description"""
        descriptions = {
            CompositionPattern.SEQUENTIAL: (
                "Execute steps in sequence, one after another"
            ),
            CompositionPattern.PARALLEL: (
                "Execute steps concurrently"
            ),
            CompositionPattern.CONDITIONAL: (
                "Execute steps based on conditions"
            ),
            CompositionPattern.DELEGATING: (
                "Delegate operations to child orchestrators"
            ),
        }
        return descriptions.get(self, "Unknown pattern")

    @property
    def use_cases(self) -> List[str]:
        """Get pattern use cases"""
        use_cases = {
            CompositionPattern.SEQUENTIAL: [
                "Multi-step workflows with dependencies",
                "Data transformation pipelines",
                "Batch processing workflows",
            ],
            CompositionPattern.PARALLEL: [
                "Independent parallel operations",
                "Bulk data loading",
                "Concurrent analysis tasks",
            ],
            CompositionPattern.CONDITIONAL: [
                "Decision trees in workflows",
                "Error handling paths",
                "A/B testing workflows",
            ],
            CompositionPattern.DELEGATING: [
                "Microservice orchestration",
                "Multi-tenant operations",
                "Hierarchical task decomposition",
            ],
        }
        return use_cases.get(self, [])

    @property
    def examples(self) -> List[str]:
        """Get pattern examples"""
        examples = {
            CompositionPattern.SEQUENTIAL: [
                "Extract -> Transform -> Load (ETL)",
                "Validate -> Process -> Archive",
            ],
            CompositionPattern.PARALLEL: [
                "Process multiple files concurrently",
                "Bulk analysis across datasets",
            ],
            CompositionPattern.CONDITIONAL: [
                "IF error THEN retry ELSE continue",
                "IF condition_met THEN path_a ELSE path_b",
            ],
            CompositionPattern.DELEGATING: [
                "Parent delegates to child orchestrators",
                "Hierarchical task distribution",
            ],
        }
        return examples.get(self, [])

    @classmethod
    def get_all(cls) -> List["CompositionPattern"]:
        """Get all composition patterns"""
        return list(cls)


@dataclass
class ComposedOrchestrator:
    """Represents a composed orchestrator"""

    name: str
    pattern: CompositionPattern
    steps: List[str] = field(default_factory=list)
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    def get_metadata(self) -> Dict[str, Any]:
        """Get composition metadata"""
        return {
            "name": self.name,
            "pattern": self.pattern.value,
            "composition_type": "composed",
            "step_count": len(self.steps),
            "created_at": self.created_at.isoformat(),
            "description": self.description,
        }

    def add_step(self, step: str) -> None:
        """Add step to composition

        Args:
            step: Step identifier to add
        """
        self.steps.append(step)

    def remove_step(self, step: str) -> None:
        """Remove step from composition

        Args:
            step: Step identifier to remove

        Raises:
            ValueError: If step not found
        """
        if step not in self.steps:
            raise ValueError(f"Step '{step}' not found in composition")
        self.steps.remove(step)

    def handle_error(self, error: Exception, step: str) -> Dict[str, Any]:
        """Handle error in composition

        Args:
            error: Exception that occurred
            step: Step where error occurred

        Returns:
            Error handling result
        """
        error_record = {
            "step": step,
            "error": str(error),
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
        }
        self.errors.append(error_record)
        return error_record

    def rollback(self) -> Dict[str, Any]:
        """Rollback composition to previous state

        Returns:
            Rollback result
        """
        return {
            "status": "rolled_back",
            "timestamp": datetime.utcnow().isoformat(),
            "errors_cleared": len(self.errors),
        }

    def get_recovery_strategies(self) -> List[str]:
        """Get available recovery strategies

        Returns:
            List of recovery strategies
        """
        strategies = [
            "retry-failed-step",
            "skip-failed-step",
            "rollback-to-checkpoint",
            "halt-and-alert",
            "use-fallback-value",
        ]
        return strategies

    def get_best_practices(self) -> List[str]:
        """Get composition best practices

        Returns:
            List of best practices
        """
        practices = [
            "Define clear step dependencies",
            "Implement comprehensive error handling",
            "Add audit logging to each step",
            "Use meaningful step identifiers",
            "Document composition intent",
            "Plan for rollback scenarios",
            "Test composition paths",
        ]
        return practices


@dataclass
class DelegationResult:
    """Result of a delegation operation"""

    delegator: str
    delegatee: str
    status: str
    output: Any = None
    errors: List[str] = field(default_factory=list)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    execution_time_ms: float = 0.0

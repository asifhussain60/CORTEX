"""
Stage Execution Strategy Pattern for MasterOrchestrator.

ENH-087 Track 1.1: Extract Stage 1-4 logic into pluggable strategies.

Authority:
- ENH-087: Orchestrator Consolidation (Strategy Pattern)
- Phase 81: Agent Architecture Redesign
- CORE-035: Single Canonical Implementation

Pattern:
    MasterOrchestrator delegates to StageExecutionStrategy implementations:
    - Stage1Strategy: Comprehension + Challenge (InteractionOrchestrator)
    - Stage2Strategy: Intent Classification (IntentRouter)
    - Stage3Strategy: Compliance Validation (GovernanceRegistry)
    - Stage4Strategy: Domain Execution (Orchestrator delegation)

Benefits:
    - Testability: Each stage independently testable
    - Extensibility: Add stages without modifying MasterOrchestrator
    - Single Responsibility: Each strategy handles one stage
    - EventBus Integration: Stages communicate via events

Governance:
    - CORE-008: TDD (tests in tests/unit/orchestrators/strategies/)
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings
    - CORE-035: Single canonical stage execution pattern

Author: Asif Hussain (ENH-087 implementation)
Created: 2026-02-11
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from cortex.core.result import Result


@dataclass
class StageContext:
    """
    Context passed between stages in orchestration pipeline.
    
    Accumulates information across stages:
    - user_request: Original user request
    - intent: Classified intent (from Stage 2)
    - confidence: Intent confidence (0.0-1.0)
    - challenge_result: Challenge generation result (from Stage 1)
    - compliance_status: Governance validation (from Stage 3)
    - domain_result: Domain execution result (from Stage 4)
    - metadata: Additional context (LENS, knowledge, etc.)
    
    Example:
        >>> context = StageContext(user_request="implement feature X")
        >>> context.intent = "IMPLEMENT"
        >>> context.confidence = 0.95
    """
    user_request: str
    intent: Optional[str] = None
    confidence: Optional[float] = None
    challenge_result: Optional[Dict[str, Any]] = None
    compliance_status: Optional[Dict[str, Any]] = None
    domain_result: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Initialize metadata dict if not provided."""
        if self.metadata is None:
            self.metadata = {}


class StageExecutionStrategy(ABC):
    """
    Abstract base class for stage execution strategies.
    
    Each stage in MasterOrchestrator's pipeline (1-4) implements this protocol:
    1. Comprehension: InteractionOrchestrator + Challenge generation
    2. Intent Classification: IntentRouter
    3. Compliance Validation: GovernanceRegistry
    4. Domain Execution: Delegate to domain orchestrators
    
    Subclasses MUST implement:
    - execute(): Core stage logic
    - get_stage_name(): Stage identifier for logging
    - get_dependencies(): Required orchestrators/services
    
    EventBus Integration:
    - Stages can emit events (STAGE_COMPLETE, STAGE_FAILED)
    - Stages can subscribe to upstream stage events
    
    Example:
        >>> strategy = Stage1ComprehensionStrategy(interaction_orch)
        >>> result = strategy.execute(context)
        >>> if result.is_ok():
        ...     context = result.unwrap()
    """
    
    @abstractmethod
    def execute(self, context: StageContext) -> Result:
        """
        Execute stage logic and update context.
        
        Args:
            context: Stage context with request and accumulated results
        
        Returns:
            Result: Updated StageContext on success, error string on failure
        
        Raises:
            NotImplementedError: If subclass doesn't implement
        """
        pass
    
    @abstractmethod
    def get_stage_name(self) -> str:
        """
        Get stage name for logging and event emission.
        
        Returns:
            str: Stage name (e.g., "Stage1_Comprehension")
        
        Example:
            >>> strategy.get_stage_name()
            "Stage1_Comprehension"
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> list[str]:
        """
        Get required dependencies for stage execution.
        
        Returns:
            list[str]: Dependency names (orchestrators, services)
        
        Example:
            >>> strategy.get_dependencies()
            ["InteractionOrchestrator", "ChallengeGenerator"]
        """
        pass
    
    def validate_dependencies(self) -> Result:
        """
        Validate that all dependencies are available.
        
        Returns:
            Result: Ok(None) if all deps available, Err with missing deps
        
        Example:
            >>> result = strategy.validate_dependencies()
            >>> if result.is_err():
            ...     print(f"Missing: {result.unwrap_err()}")
        """
        from cortex.core.result import Ok, Err
        
        missing = []
        for dep in self.get_dependencies():
            if not hasattr(self, dep.lower().replace("orchestrator", "_orch")):
                missing.append(dep)
        
        if missing:
            return Err(f"Missing dependencies: {', '.join(missing)}")
        
        return Ok(None)

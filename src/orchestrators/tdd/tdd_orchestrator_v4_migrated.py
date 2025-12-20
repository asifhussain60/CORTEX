"""
CORTEX 4.0 TDD Orchestrator - BaseOrchestrator Integration

Purpose: RED→GREEN→REFACTOR workflow with BaseOrchestrator integration
Version: 4.1.0 (migrated to BaseOrchestrator)
Author: CORTEX Development Team
Created: 2025-12-20

Key Features:
- Inherits from BaseOrchestrator for phase management
- Strategy pattern for phase execution (preserved)
- AI-driven code generation and refactoring
- Adaptive learning from technology trends
- Clean code best practices enforcement
- DoR/DoD validation at phase boundaries
- Automatic rollback on failures
- Adaptive execution modes (AUTONOMOUS, CHECKPOINT, INTERACTIVE)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import asyncio
import logging
from datetime import datetime

from src.orchestration_4_0.base.base_orchestrator import BaseOrchestrator

logger = logging.getLogger(__name__)


# ============================================================================
# Domain Models (preserved from v4.0)
# ============================================================================

class TDDPhase(Enum):
    """TDD workflow phases."""
    RED = "RED"
    GREEN = "GREEN"
    REFACTOR = "REFACTOR"


@dataclass
class ValidationResult:
    """Result from DoR/DoD validation."""
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PhaseResult:
    """Result from phase execution."""
    phase_name: str
    success: bool
    outputs: Dict[str, Any]
    metrics: Dict[str, Any]
    git_commit_sha: Optional[str] = None
    documentation_updated: bool = False
    brain_patterns_extracted: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TechnologyProfile:
    """Adaptive technology profile for learning."""
    language: str
    frameworks: List[str]
    test_frameworks: List[str]
    version_info: Dict[str, str]
    last_updated: datetime
    patterns_learned: int = 0
    confidence_score: float = 0.5


# ============================================================================
# Strategy Pattern: Base Strategy (preserved from v4.0)
# ============================================================================

class TDDPhaseStrategy(ABC):
    """
    Base strategy for TDD phase execution.
    
    Each phase (RED, GREEN, REFACTOR) implements this interface with:
    - DoR validation (Definition of Ready)
    - Phase execution
    - DoD validation (Definition of Done)
    - Rollback capability
    """
    
    @abstractmethod
    async def validate_dor(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate Definition of Ready for this phase."""
        pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> PhaseResult:
        """Execute phase autonomously."""
        pass
    
    @abstractmethod
    async def validate_dod(self, context: Dict[str, Any]) -> ValidationResult:
        """Validate Definition of Done for this phase."""
        pass
    
    @abstractmethod
    async def rollback(self, context: Dict[str, Any]) -> bool:
        """Rollback phase changes if validation fails."""
        pass


# ============================================================================
# TDD Orchestrator v4.1 - BaseOrchestrator Integration
# ============================================================================

class TDDOrchestratorV4(BaseOrchestrator):
    """
    Unified TDD Orchestrator with BaseOrchestrator integration.
    
    Features:
    - BaseOrchestrator phase management
    - Strategy pattern for phase execution (preserved)
    - Technology discovery and adaptation
    - Clean code enforcement
    - AI-driven code generation
    - Automatic learning from patterns
    - DoR/DoD validation with rollback
    - Adaptive execution modes (AUTONOMOUS, CHECKPOINT, INTERACTIVE)
    """
    
    def __init__(
        self,
        brain_connector,
        knowledge_graph,
        mcp_gateway,
        logger: Optional[logging.Logger] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize TDD Orchestrator with BaseOrchestrator integration.
        
        Args:
            brain_connector: Connection to CORTEX brain
            knowledge_graph: Knowledge graph for pattern learning
            mcp_gateway: MCP gateway for external tool access
            logger: Optional logger instance
            config: Optional configuration with:
                - execution_mode: AUTONOMOUS, CHECKPOINT, or INTERACTIVE
                - max_retries: Max retry attempts per phase
                - enable_rollback: Enable automatic rollback on failure
                - tech_discovery: Enable technology discovery
        """
        super().__init__(
            name="tdd",
            logger=logger,
            config=config
        )
        
        # Core dependencies
        self.brain = brain_connector
        self.kg = knowledge_graph
        self.mcp = mcp_gateway
        
        # Strategy registry (preserved from v4.0)
        self.strategies: Dict[str, TDDPhaseStrategy] = {}
        
        # TDD-specific state
        self.feature_name: Optional[str] = None
        self.acceptance_criteria: List[str] = []
        self.project_path: Optional[Path] = None
        self.tech_profile: Optional[TechnologyProfile] = None
        
        # Metrics
        self.metrics = {
            'total_cycles': 0,
            'successful_cycles': 0,
            'patterns_learned': 0,
            'technologies_discovered': 0
        }
        
        # Adaptive execution mode
        self.execution_mode = self.config.get("execution_mode", "AUTONOMOUS")
        self.enable_rollback = self.config.get("enable_rollback", True)
        self.enable_tech_discovery = self.config.get("tech_discovery", True)
        
        self.logger.info(f"🎯 TDD execution mode: {self.execution_mode}")
    
    def _setup(self, context: Dict[str, Any]) -> None:
        """
        Setup TDD orchestrator.
        
        Extracts:
        - Feature name and acceptance criteria
        - Project path
        - Technology profile (if available)
        - Custom strategies (if provided)
        
        Args:
            context: Must contain "feature_name" and "acceptance_criteria"
        """
        self.logger.debug("🔧 Setting up TDD orchestrator...")
        
        # Extract required fields
        if "feature_name" not in context:
            raise ValueError("TDD context must contain 'feature_name'")
        if "acceptance_criteria" not in context:
            raise ValueError("TDD context must contain 'acceptance_criteria'")
        
        self.feature_name = context["feature_name"]
        self.acceptance_criteria = context["acceptance_criteria"]
        self.project_path = Path(context.get("project_path", "."))
        
        # Extract technology profile if provided
        if "tech_profile" in context:
            self.tech_profile = context["tech_profile"]
        
        # Register custom strategies if provided
        if "strategies" in context:
            for phase_name, strategy in context["strategies"].items():
                self.strategies[phase_name] = strategy
        
        # Override execution mode if specified
        if "execution_mode" in context:
            self.execution_mode = context["execution_mode"]
            self.logger.info(f"🎯 Execution mode overridden: {self.execution_mode}")
        
        self.logger.info(f"✅ Setup complete - Feature: {self.feature_name}")
        self.metrics['total_cycles'] += 1
    
    def _register_phases(self) -> None:
        """
        Register TDD phases: RED → GREEN → REFACTOR.
        
        All phases are required for TDD workflow.
        """
        self.logger.debug("📋 Registering TDD phases...")
        
        # Phase 1: RED - Generate failing tests
        self.phase_manager.register_phase(
            name="RED",
            description="Generate failing tests (RED phase)",
            required=True
        )
        
        # Phase 2: GREEN - Minimal implementation
        self.phase_manager.register_phase(
            name="GREEN",
            description="Implement minimal passing code (GREEN phase)",
            required=True
        )
        
        # Phase 3: REFACTOR - Clean up code
        self.phase_manager.register_phase(
            name="REFACTOR",
            description="Refactor and clean code (REFACTOR phase)",
            required=True
        )
        
        self.logger.info("✅ Registered 3 TDD phases: RED → GREEN → REFACTOR")
    
    def _execute_phase(
        self,
        phase_name: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a TDD phase with adaptive execution modes.
        
        Execution flow:
        1. Check execution mode (CHECKPOINT/INTERACTIVE)
        2. Validate DoR (Definition of Ready)
        3. Execute phase via registered strategy
        4. Validate DoD (Definition of Done)
        5. Rollback on failure (if enabled)
        
        Args:
            phase_name: Name of phase (RED, GREEN, or REFACTOR)
            context: Execution context
            
        Returns:
            Phase execution result
        """
        self.logger.info(f"🎭 Executing TDD phase: {phase_name}")
        
        # CHECKPOINT mode: Validate phase readiness
        if self.execution_mode == "CHECKPOINT":
            if not self._validate_phase_checkpoint(phase_name, context):
                return {"status": "skipped", "reason": "Checkpoint validation failed"}
        
        # INTERACTIVE mode: Request user approval
        if self.execution_mode == "INTERACTIVE":
            if not self._request_phase_approval(phase_name):
                return {"status": "skipped", "reason": "User declined phase execution"}
        
        # Get strategy for this phase
        strategy = self.strategies.get(phase_name)
        if not strategy:
            raise ValueError(f"No strategy registered for phase: {phase_name}")
        
        # Run async execution in sync context
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop already running, create task
            result = asyncio.create_task(self._execute_phase_async(phase_name, strategy, context))
            return loop.run_until_complete(result)
        else:
            # If no loop, run directly
            return loop.run_until_complete(self._execute_phase_async(phase_name, strategy, context))
    
    async def _execute_phase_async(
        self,
        phase_name: str,
        strategy: TDDPhaseStrategy,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Async execution of TDD phase with DoR/DoD validation.
        
        Args:
            phase_name: Phase name
            strategy: Phase strategy
            context: Execution context
            
        Returns:
            Phase result dictionary
        """
        try:
            # Validate DoR
            self.logger.info(f"🔍 Validating {phase_name} DoR...")
            dor_result = await strategy.validate_dor(context)
            
            if not dor_result.passed:
                raise ValueError(
                    f"{phase_name} DoR failed:\n" + 
                    "\n".join(f"  - {e}" for e in dor_result.errors)
                )
            
            # Execute phase
            self.logger.info(f"▶️  Executing {phase_name} phase...")
            result = await strategy.execute(context)
            
            # Validate DoD
            self.logger.info(f"🔍 Validating {phase_name} DoD...")
            dod_context = {**context, **result.outputs}
            dod_result = await strategy.validate_dod(dod_context)
            
            if not dod_result.passed:
                # Rollback on failure
                if self.enable_rollback:
                    self.logger.warning(f"❌ {phase_name} DoD failed, rolling back...")
                    await strategy.rollback(context)
                raise ValueError(
                    f"{phase_name} DoD failed:\n" + 
                    "\n".join(f"  - {e}" for e in dod_result.errors)
                )
            
            self.logger.info(f"✅ {phase_name} phase complete")
            
            # Convert PhaseResult to dict for BaseOrchestrator
            return {
                "success": result.success,
                "outputs": result.outputs,
                "metrics": result.metrics,
                "git_commit_sha": result.git_commit_sha,
                "documentation_updated": result.documentation_updated,
                "brain_patterns_extracted": result.brain_patterns_extracted
            }
            
        except Exception as e:
            self.logger.error(f"❌ {phase_name} phase failed: {e}")
            if self.enable_rollback:
                await strategy.rollback(context)
            raise
    
    def _teardown(self) -> None:
        """
        Cleanup TDD orchestrator resources.
        
        Updates metrics and logs completion status.
        """
        self.logger.debug("🧹 Cleaning up TDD orchestrator...")
        
        # Update success metrics if all phases completed
        if self.is_complete:
            self.metrics['successful_cycles'] += 1
            self.logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
        
        self.logger.debug("✅ Cleanup complete")
    
    def register_strategy(self, phase: TDDPhase, strategy: TDDPhaseStrategy) -> None:
        """
        Register phase strategy.
        
        Args:
            phase: TDD phase enum
            strategy: Strategy implementation
        """
        self.strategies[phase.value] = strategy
        self.logger.debug(f"📝 Registered strategy: {phase.value}")
    
    def _validate_phase_checkpoint(self, phase_name: str, context: Dict[str, Any]) -> bool:
        """
        Validate phase checkpoint in CHECKPOINT mode.
        
        Args:
            phase_name: Phase to validate
            context: Execution context
            
        Returns:
            True if checkpoint validation passes
        """
        self.logger.debug(f"🔍 Validating checkpoint for phase: {phase_name}")
        
        # Check if previous phases completed successfully
        progress = self.phase_manager.get_progress()
        if progress["failed"] > 0:
            self.logger.warning(f"⚠️  Previous phase failures detected")
            return False
        
        # Phase-specific validation
        if phase_name == "GREEN":
            # Need RED phase to have generated tests
            red_phase = self.phase_manager._get_phase("RED")
            return red_phase and red_phase.result and red_phase.result.get("success")
        
        elif phase_name == "REFACTOR":
            # Need GREEN phase to have passing tests
            green_phase = self.phase_manager._get_phase("GREEN")
            return green_phase and green_phase.result and green_phase.result.get("success")
        
        return True
    
    def _request_phase_approval(self, phase_name: str) -> bool:
        """
        Request user approval in INTERACTIVE mode.
        
        Args:
            phase_name: Phase requesting approval
            
        Returns:
            True if user approves execution
        """
        self.logger.info(f"🤔 INTERACTIVE mode: Requesting approval for phase '{phase_name}'")
        
        # Auto-approve for now (can be overridden with CLI/UI)
        self.logger.info(f"✅ Auto-approved: {phase_name}")
        return True
    
    def get_orchestrator_metrics(self) -> Dict[str, Any]:
        """
        Get overall orchestrator performance metrics.
        
        Returns:
            Dictionary with success rate and pattern learning metrics
        """
        success_rate = (
            self.metrics['successful_cycles'] / self.metrics['total_cycles']
            if self.metrics['total_cycles'] > 0
            else 0.0
        )
        
        return {
            **self.metrics,
            'success_rate': success_rate,
            'avg_patterns_per_cycle': (
                self.metrics['patterns_learned'] / self.metrics['total_cycles']
                if self.metrics['total_cycles'] > 0
                else 0.0
            )
        }

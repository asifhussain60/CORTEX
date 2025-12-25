"""
CORTEX 4.0 Planning Orchestrator - Core Module

Purpose: Orchestrates YAML-based feature planning with validation and autonomous execution
Version: 4.0.0
Author: CORTEX Development Team
Migrated: 2025-12-19 (from legacy 5,557 LOC → 3,000 LOC MVP in Week 8-9)

Key Features (Week 8 Core MVP):
- BaseOrchestrator integration with PhaseManager
- YAML plan validation against schema
- Plan generation with complexity analysis
- Markdown rendering for human-readable plans
- DoR/DoD validation at phase boundaries
- TDD workflow integration
- Git checkpoint support
- Session management for restoration

Deferred to Week 9 (Intelligence Layer):
- TestIntelligence integration (coverage analysis)
- TDDIntelligence integration (workflow enforcement)
- ValidationFramework integration (multi-layer validation)
- Manifest compliance validation

Deferred to Week 11+ (Advanced Features):
- Threat modeling integration (requires Phase 2.5 agentic AI)
- Architecture review integration (requires Phase 2.5 agentic AI)
- Task injection system (requires orchestration_4_0)
- Orchestration checkpoints (requires orchestration_4_0)
- Incremental plan generation (requires adaptive reasoning)
- Folder-based plans (requires enhanced context discovery)

Architecture:
- Core: planning_orchestrator.py (this file - main workflow)
- Validation: plan_validator.py (YAML schema validation)
- Generation: plan_generator.py (plan creation logic)
- Rendering: markdown_renderer.py (Markdown export)
- Execution: plan_executor.py (autonomous execution - Day 3)
- Integration: phase_manager_integration.py (PhaseManager wiring - Day 3)
- Git: git_checkpoint_integration.py (git checkpoints - Day 3)
- Session: session_manager.py (session restoration - Day 3)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import yaml

from src.orchestrators.base.base_orchestrator import (
    BaseOrchestrator,
    OrchestratorResult,
    OrchestratorStatus,
    ValidationResult as BaseValidationResult
)

# Week 8 Day 3: Import execution engine modules
from src.orchestrators.planning.plan_executor import (
    PlanExecutor,
    ExecutionMode,
    ExecutionResult
)
from src.orchestrators.planning.phase_manager_integration import PhaseManagerIntegration
from src.orchestrators.planning.git_checkpoint_integration import (
    GitCheckpointManager,
    CheckpointType
)
from src.orchestrators.planning.session_manager import (
    SessionManager,
    SessionStatus
)

# Week 9: Intelligence Layer Adapters
from src.orchestrators.planning.intelligence import (
    TestIntelligenceAdapter,
    TDDIntelligenceAdapter,
    ValidationFrameworkAdapter,
    ManifestComplianceValidator
)

# Phase 10: YAML Modularization
from src.orchestrators.planning.markdown_renderer import MarkdownRenderer

logger = logging.getLogger(__name__)


# ============================================================================
# Domain Models
# ============================================================================

class PlanningPhase(Enum):
    """Planning workflow phases."""
    DISCOVERY = "DISCOVERY"           # Pre-planning context gathering
    VALIDATION = "VALIDATION"         # Schema and DoR validation
    GENERATION = "GENERATION"         # Plan creation
    RENDERING = "RENDERING"           # Markdown export
    EXECUTION = "EXECUTION"           # Autonomous execution (Week 8 Day 3)


class PlanComplexity(Enum):
    """Plan complexity tiers for adaptive planning."""
    LOW = 1          # Skeleton plan (DoR/DoD only)
    MEDIUM = 2       # Conditional plan (some phases detailed)
    HIGH = 3         # Incremental plan (all phases detailed)
    CRITICAL = 4     # Full plan with security analysis


class PlanType(Enum):
    """Plan generation types."""
    SKELETON = "skeleton"           # DoR/DoD only
    CONDITIONAL = "conditional"     # Conditional phases
    INCREMENTAL = "incremental"     # Full incremental
    FOLDER_BASED = "folder_based"   # Deferred to Week 11


@dataclass
class PlanMetadata:
    """Plan metadata structure."""
    title: str
    description: str
    complexity: PlanComplexity
    plan_type: PlanType
    author: str = "CORTEX Planning System 4.0"
    created: datetime = field(default_factory=datetime.now)
    version: str = "4.0.0"
    tags: List[str] = field(default_factory=list)
    estimated_duration: Optional[str] = None


@dataclass
class PlanPhaseData:
    """Plan phase structure."""
    phase_name: str
    tasks: List[Dict[str, Any]]
    acceptance_criteria: List[str]
    estimated_duration: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    is_conditional: bool = False
    condition: Optional[str] = None


@dataclass
class PlanData:
    """Complete plan data structure."""
    metadata: PlanMetadata
    definition_of_ready: List[str]
    definition_of_done: List[str]
    phases: List[PlanPhaseData]
    tdd_requirements: Optional[Dict[str, List[str]]] = None
    git_checkpoint_strategy: Optional[Dict[str, Any]] = None
    session_metadata: Optional[Dict[str, Any]] = None


@dataclass
class ValidationResult:
    """Result of plan validation (extends base)."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_type: str = "plan_validation"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_base_validation_result(self) -> BaseValidationResult:
        """Convert to BaseOrchestrator ValidationResult."""
        return BaseValidationResult(
            valid=self.valid,
            errors=self.errors,
            warnings=self.warnings
        )


@dataclass
class PlanningResult:
    """Result of planning orchestrator execution."""
    success: bool
    plan_data: Optional[PlanData]
    plan_path: Optional[Path]
    markdown_path: Optional[Path]
    validation_result: Optional[ValidationResult]
    execution_summary: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Planning Orchestrator (Week 8 Core MVP)
# ============================================================================

class PlanningOrchestrator(BaseOrchestrator):
    """
    CORTEX 4.0 Planning Orchestrator - Core MVP.
    
    Responsibilities (Week 8):
    - Initialize with BaseOrchestrator pattern
    - Load and validate YAML schema
    - Coordinate plan validation (via PlanValidator)
    - Coordinate plan generation (via PlanGenerator)
    - Coordinate markdown rendering (via MarkdownRenderer)
    - Manage planning workflow phases
    - Integrate with PhaseManager (Day 3)
    - Support git checkpoints (Day 3)
    - Support session restoration (Day 3)
    
    Deferred to Week 9:
    - Test intelligence integration
    - TDD intelligence integration
    - Validation framework integration
    - Manifest compliance validation
    
    Deferred to Week 11+:
    - Threat modeling integration
    - Architecture review integration
    - Task injection system
    - Advanced checkpoint management
    - Incremental generation
    - Folder-based plans
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Planning Orchestrator.
        
        Args:
            config: Orchestrator configuration
                Required keys:
                - cortex_root: Path to CORTEX root directory
                Optional keys:
                - schema_path: Custom schema path (default: cortex-brain/config/plan-schema.yaml)
                - plans_dir: Custom plans directory (default: cortex-brain/documents/planning/features)
                - enable_git_checkpoints: Enable git checkpoints (default: True)
                - enable_session_restoration: Enable session restoration (default: True)
        """
        # Set name and version before BaseOrchestrator.__init__
        config["name"] = "PlanningOrchestrator"
        config["version"] = "4.0.0"
        
        super().__init__(config)
        
        # Path configuration
        self.cortex_root = Path(config["cortex_root"])
        self.schema_path = Path(config.get(
            "schema_path",
            self.cortex_root / "cortex-brain" / "config" / "plan-schema.yaml"
        ))
        self.plans_dir = Path(config.get(
            "plans_dir",
            self.cortex_root / "cortex-brain" / "documents" / "planning" / "features"
        ))
        self.active_plans_dir = self.plans_dir / "active"
        self.completed_plans_dir = self.plans_dir / "completed"
        
        # Feature flags
        self.git_checkpoints_enabled = config.get("enable_git_checkpoints", True)
        self.session_restoration_enabled = config.get("enable_session_restoration", True)
        self.checkpoint_retention_limit = config.get("checkpoint_retention_limit", 10)
        self.checkpoint_strategy = config.get("checkpoint_strategy", "per_phase")
        
        # Initialize schema
        self.schema = self._load_schema()
        
        # Week 8 Day 3: Initialize execution engine modules
        self.plan_validator = None      # Will be: from .plan_validator import PlanValidator
        self.plan_generator = None      # Will be: from .plan_generator import PlanGenerator
        
        # Phase 10: Initialize MarkdownRenderer with modularization support
        modularization_threshold = config.get("planning", {}).get(
            "yaml_modularization_threshold_bytes", 
            20480  # Default: 20KB
        )
        self.markdown_renderer = MarkdownRenderer(
            output_dir=self.active_plans_dir,
            modularization_threshold=modularization_threshold
        )
        
        # Execution engine (Week 8 Day 3)
        self.plan_executor = PlanExecutor(
            workspace_root=config.get("workspace_root", Path.cwd()),
            execution_mode=ExecutionMode[config.get("execution_mode", "SUPERVISED").upper()],
            logger_instance=self.logger
        ) if config.get("enable_autonomous_execution", True) else None
        
        self.phase_manager = PhaseManagerIntegration(
            orchestrator=self,
            workspace_root=config.get("workspace_root", Path.cwd()),
            logger_instance=self.logger
        )
        
        self.git_checkpoint = GitCheckpointManager(
            workspace_root=config.get("workspace_root", Path.cwd()),
            checkpoint_prefix="cortex-plan-checkpoint",
            logger_instance=self.logger
        ) if self.git_checkpoints_enabled else None
        
        # Fallback in-memory checkpoints for testing (when git not available)
        # Initialize regardless, will be used if git is not available
        self._memory_checkpoints = []
        self._checkpoint_counter = 0
        
        self.session_manager = SessionManager(
            workspace_root=config.get("workspace_root", Path.cwd()),
            logger_instance=self.logger
        ) if self.session_restoration_enabled else None
        
        # Week 9: Initialize Intelligence Layer Adapters
        self.test_intelligence = TestIntelligenceAdapter(
            project_root=config.get("workspace_root", Path.cwd())
        ) if config.get("enable_test_intelligence", True) else None
        
        self.tdd_intelligence = TDDIntelligenceAdapter(
            project_root=config.get("workspace_root", Path.cwd()),
            enforce_strict=config.get("tdd_strict_mode", True)
        ) if config.get("enable_tdd_intelligence", True) else None
        
        self.validation_framework = ValidationFrameworkAdapter(
            strict_mode=config.get("validation_strict_mode", True)
        ) if config.get("enable_validation_framework", True) else None
        
        self.manifest_validator = ManifestComplianceValidator(
            manifest_path=config.get("manifest_path")
        ) if config.get("enable_manifest_validation", True) else None
        
        # Planning state
        self.current_phase = None
        self.planning_mode_active = False
        self.current_session = None
        
        # TDD requirements (SKULL enforcement)
        self._tdd_dor_requirements = [
            "TDD Mastery workflow MUST be followed (RED→GREEN→REFACTOR)",
            "Tests MUST fail before implementation (RED phase validation)",
            "All CORTEX brain protection rules apply (SKULL enforcement)",
            "Reference: cortex-brain/brain-protection-rules.yaml for complete ruleset"
        ]
        
        self._tdd_dod_requirements = [
            "All code follows TDD workflow with git checkpoints at phase boundaries",
            "No SKULL rule violations detected (brain protection compliance verified)",
            "Test coverage meets CORTEX standards (RED→GREEN→REFACTOR documented)",
            "Git history shows test-first commits (RED phase before GREEN phase)"
        ]
        
        self.logger.info(f"✅ Planning Orchestrator 4.0 initialized (schema={'loaded' if self.schema else 'not_found'})")
    
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load plan schema from YAML file.
        
        Returns:
            Schema dictionary or None if not found
        """
        try:
            if not self.schema_path.exists():
                self.logger.warning(f"Schema not found at {self.schema_path}, using minimal defaults")
                return self._get_default_schema()
            
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)
                self.logger.info(f"✅ Schema loaded: {self.schema_path.name}")
                return schema
        except Exception as e:
            self.logger.error(f"Failed to load schema: {e}")
            return self._get_default_schema()
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """
        Return minimal default schema if file not found.
        
        Returns:
            Minimal schema dictionary
        """
        return {
            "schema": {
                "version": "1.0.0",
                "required_fields": ["metadata", "phases", "definition_of_ready", "definition_of_done"]
            }
        }
    
    def validate_input(self, **kwargs) -> BaseValidationResult:
        """
        Validate input parameters for planning orchestrator.
        
        Args:
            **kwargs: Input parameters
                Required: feature_name OR plan_data
                Optional: plan_type, complexity, output_dir
        
        Returns:
            BaseValidationResult with validation status
        """
        errors = []
        warnings = []
        
        # Check required parameters
        if "feature_name" not in kwargs and "plan_data" not in kwargs:
            errors.append("Either 'feature_name' or 'plan_data' must be provided")
        
        # Validate plan_type if provided
        if "plan_type" in kwargs:
            try:
                PlanType(kwargs["plan_type"])
            except ValueError:
                valid_types = [t.value for t in PlanType]
                errors.append(f"Invalid plan_type '{kwargs['plan_type']}'. Valid: {valid_types}")
        
        # Validate complexity if provided
        if "complexity" in kwargs:
            try:
                if isinstance(kwargs["complexity"], int):
                    PlanComplexity(kwargs["complexity"])
                else:
                    # Try to match by name
                    PlanComplexity[kwargs["complexity"].upper()]
            except (ValueError, KeyError):
                warnings.append(f"Invalid complexity '{kwargs['complexity']}'. Will auto-detect.")
        
        # Validate schema is loaded
        if not self.schema:
            warnings.append("Schema not loaded - validation may be limited")
        
        # Validate output directory exists
        if "output_dir" in kwargs:
            output_dir = Path(kwargs["output_dir"])
            if not output_dir.exists():
                warnings.append(f"Output directory does not exist: {output_dir}")
        
        return BaseValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def execute(self, **kwargs) -> OrchestratorResult:
        """
        Execute planning orchestrator workflow.
        
        Workflow (Week 8 MVP):
        1. DISCOVERY: Gather context (placeholder for Week 11 advanced features)
        2. VALIDATION: Validate input and schema
        3. GENERATION: Generate plan (or validate provided plan)
        4. RENDERING: Render markdown view
        5. EXECUTION: Execute plan autonomously (Day 3)
        
        Args:
            **kwargs: Execution parameters
                feature_name: Name of feature to plan (str)
                plan_data: Pre-generated plan data (Dict) - alternative to feature_name
                plan_type: Type of plan to generate (PlanType enum or str)
                complexity: Plan complexity (PlanComplexity enum or int)
                output_dir: Custom output directory (Path or str)
                auto_execute: Execute plan after generation (bool, default: False - Day 3)
        
        Returns:
            OrchestratorResult with execution status and planning result
        """
        self.status = OrchestratorStatus.RUNNING
        self.start_time = datetime.now()
        
        try:
            # Phase 1: DISCOVERY (placeholder - Week 11 will add architectural review)
            self.current_phase = PlanningPhase.DISCOVERY
            self.logger.info("🎭 Phase transition: START → DISCOVERY")
            
            feature_name = kwargs.get("feature_name")
            plan_data_input = kwargs.get("plan_data")
            
            # Week 11: Add architectural review, threat modeling, context discovery
            # For now, just log
            self.logger.info(f"📋 Planning for: {feature_name or 'provided plan data'}")
            
            # Phase 2: VALIDATION
            self.current_phase = PlanningPhase.VALIDATION
            self.logger.info("🎭 Phase transition: DISCOVERY → VALIDATION")
            
            if plan_data_input:
                # Validate provided plan data
                validation_result = self._validate_plan_data(plan_data_input)
                if not validation_result.valid:
                    return self._create_error_result(
                        f"Plan validation failed: {', '.join(validation_result.errors)}",
                        validation_result=validation_result
                    )
                plan_data = plan_data_input
            else:
                # Will validate during generation
                plan_data = None
            
            # Phase 3: GENERATION
            self.current_phase = PlanningPhase.GENERATION
            self.logger.info("🎭 Phase transition: VALIDATION → GENERATION")
            
            if not plan_data:
                # Generate new plan
                generation_result = self._generate_plan(
                    feature_name=feature_name,
                    plan_type=kwargs.get("plan_type", "incremental"),
                    complexity=kwargs.get("complexity")
                )
                if not generation_result.success:
                    return self._create_error_result(
                        f"Plan generation failed: {', '.join(generation_result.errors)}",
                        validation_result=None
                    )
                plan_data = generation_result.plan_data
            
            # Phase 4: RENDERING
            self.current_phase = PlanningPhase.RENDERING
            self.logger.info("🎭 Phase transition: GENERATION → RENDERING")
            
            rendering_result = self._render_markdown(
                plan_data=plan_data,
                output_dir=kwargs.get("output_dir", self.active_plans_dir)
            )
            if not rendering_result.success:
                return self._create_error_result(
                    f"Markdown rendering failed: {', '.join(rendering_result.errors)}",
                    validation_result=None
                )
            
            # Phase 5: EXECUTION (Week 8 Day 3 - autonomous execution)
            execution_summary = None
            if kwargs.get("auto_execute", False):
                self.current_phase = PlanningPhase.EXECUTION
                self.logger.info("🎭 Phase transition: RENDERING → EXECUTION")
                
                # Week 8 Day 3: Integrate PlanExecutor
                if self.plan_executor:
                    # Create session if session management enabled
                    if self.session_manager:
                        session = self.session_manager.create_session(
                            plan_name=feature_name or "provided_plan",
                            plan_path=rendering_result.plan_path,
                            execution_config={
                                "execution_mode": self.plan_executor.execution_mode.value,
                                "auto_checkpoint": self.git_checkpoints_enabled
                            }
                        )
                        self.current_session = session
                        self.logger.info(f"✅ Execution session created: {session.session_id}")
                    
                    # Execute plan autonomously
                    execution_result: ExecutionResult = self.plan_executor.execute_plan(
                        plan_data=plan_data,
                        plan_path=rendering_result.plan_path,
                        auto_checkpoint=self.git_checkpoints_enabled,
                        resume_from_phase=None
                    )
                    
                    # Update session if successful
                    if self.session_manager and self.current_session:
                        self.session_manager.complete_session(
                            session_id=self.current_session.session_id,
                            success=execution_result.success
                        )
                    
                    execution_summary = {
                        "status": "completed" if execution_result.success else "failed",
                        "message": execution_result.message,
                        "phases_executed": len(execution_result.phase_results),
                        "execution_time_seconds": execution_result.total_execution_time_seconds,
                        "checkpoint_created": execution_result.checkpoint_created,
                        "rollback_available": execution_result.rollback_available
                    }
                    
                    if not execution_result.success:
                        self.logger.error(f"❌ Plan execution failed: {execution_result.message}")
                        return self._create_error_result(
                            f"Plan execution failed: {execution_result.message}",
                            validation_result=None
                        )
                else:
                    self.logger.warning("⚠️  PlanExecutor not initialized - skipping autonomous execution")
                    execution_summary = {"status": "skipped", "reason": "PlanExecutor not enabled"}
            
            # Create successful result
            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds()
            
            planning_result = PlanningResult(
                success=True,
                plan_data=plan_data,
                plan_path=rendering_result.plan_path,
                markdown_path=rendering_result.markdown_path,
                validation_result=rendering_result.validation_result,
                execution_summary=execution_summary
            )
            
            self.status = OrchestratorStatus.COMPLETED
            self.logger.info("🎭 Orchestrator completing: ✅ PLANNING COMPLETE")
            
            return OrchestratorResult(
                status=OrchestratorStatus.COMPLETED,
                success=True,
                message=f"Planning complete: {feature_name or 'provided plan'}",
                data={
                    "planning_result": planning_result,
                    "plan_path": str(rendering_result.plan_path) if rendering_result.plan_path else None,
                    "markdown_path": str(rendering_result.markdown_path) if rendering_result.markdown_path else None
                },
                execution_time_seconds=execution_time
            )
        
        except Exception as e:
            self.logger.error(f"❌ Planning orchestrator failed: {e}", exc_info=True)
            self.status = OrchestratorStatus.FAILED
            return self._create_error_result(str(e), validation_result=None)
    
    def _validate_plan_data(self, plan_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate plan data against schema.
        
        Week 8 Day 1-2: Placeholder - will be delegated to PlanValidator module.
        
        Args:
            plan_data: Plan data dictionary to validate
        
        Returns:
            ValidationResult with validation status
        """
        # Day 1-2: Basic validation
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ["metadata", "phases", "definition_of_ready", "definition_of_done"]
        for field in required_fields:
            if field not in plan_data:
                errors.append(f"Missing required field: {field}")
        
        # Check metadata structure
        if "metadata" in plan_data:
            metadata = plan_data["metadata"]
            if not isinstance(metadata, dict):
                errors.append("metadata must be a dictionary")
            else:
                required_metadata = ["title", "description", "complexity"]
                for field in required_metadata:
                    if field not in metadata:
                        warnings.append(f"Missing recommended metadata field: {field}")
        
        # Day 2: Will delegate to PlanValidator module for comprehensive validation
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            validation_type="basic_plan_validation"
        )
    
    def _generate_plan(
        self,
        feature_name: str,
        plan_type: str,
        complexity: Optional[Any]
    ) -> PlanningResult:
        """
        Generate new plan.
        
        Week 8 Day 1-2: Placeholder - will be delegated to PlanGenerator module.
        
        Args:
            feature_name: Name of feature to plan
            plan_type: Type of plan to generate
            complexity: Plan complexity level
        
        Returns:
            PlanningResult with generated plan
        """
        # Day 1-2: Basic plan generation
        self.logger.info(f"📝 Generating {plan_type} plan for: {feature_name}")
        
        # Create basic plan structure
        plan_data = PlanData(
            metadata=PlanMetadata(
                title=feature_name,
                description=f"Implementation plan for {feature_name}",
                complexity=PlanComplexity.MEDIUM,  # Default
                plan_type=PlanType(plan_type)
            ),
            definition_of_ready=[
                "Requirements clearly defined",
                "Architecture design reviewed",
                "Test strategy defined"
            ],
            definition_of_done=[
                "All tests passing",
                "Code reviewed and merged",
                "Documentation updated"
            ],
            phases=[
                PlanPhaseData(
                    phase_name="Implementation",
                    tasks=[
                        {"task": "Implement core functionality", "estimated_hours": 4},
                        {"task": "Write unit tests", "estimated_hours": 2}
                    ],
                    acceptance_criteria=[
                        "Core functionality working",
                        "Tests passing"
                    ]
                )
            ],
            tdd_requirements={
                "dor": self._tdd_dor_requirements,
                "dod": self._tdd_dod_requirements
            }
        )
        
        # Day 2: Will delegate to PlanGenerator module for sophisticated generation
        
        return PlanningResult(
            success=True,
            plan_data=plan_data,
            plan_path=None,  # Will be set during rendering
            markdown_path=None,  # Will be set during rendering
            validation_result=ValidationResult(valid=True)
        )
    
    def _render_markdown(
        self,
        plan_data: PlanData,
        output_dir: Path
    ) -> PlanningResult:
        """
        Render plan as markdown with Phase 10 YAML modularization.
        
        Args:
            plan_data: Plan data to render
            output_dir: Output directory for markdown file
        
        Returns:
            PlanningResult with markdown file path and optional modular YAML structure
        """
        self.logger.info(f"📄 Rendering markdown to: {output_dir}")
        
        # Create output paths
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename from plan title
        safe_title = plan_data.metadata.title.lower().replace(" ", "-").replace("_", "-")
        
        # Phase 10: Use MarkdownRenderer with automatic YAML modularization
        # Convert PlanData to dict for renderer
        plan_dict = {
            "metadata": {
                "title": plan_data.metadata.title,
                "description": plan_data.metadata.description,
                "complexity": plan_data.metadata.complexity.value if hasattr(plan_data.metadata.complexity, 'value') else plan_data.metadata.complexity,
                "plan_type": plan_data.metadata.plan_type.value if hasattr(plan_data.metadata.plan_type, 'value') else plan_data.metadata.plan_type,
                "author": plan_data.metadata.author,
                "created": plan_data.metadata.created.isoformat() if hasattr(plan_data.metadata.created, 'isoformat') else str(plan_data.metadata.created),
                "version": plan_data.metadata.version,
            },
            "definition_of_ready": plan_data.definition_of_ready,
            "definition_of_done": plan_data.definition_of_done,
            "phases": [
                {
                    "phase_name": phase.phase_name,
                    "tasks": [{"task_name": t} for t in phase.tasks] if phase.tasks else [],
                    "acceptance_criteria": phase.acceptance_criteria,
                    "dependencies": phase.dependencies,
                }
                for phase in plan_data.phases
            ],
        }
        
        if plan_data.tdd_requirements:
            plan_dict["tdd_requirements"] = plan_data.tdd_requirements
        
        # Render with automatic modularization
        rendering_result = self.markdown_renderer.render(
            plan_data=plan_dict,
            output_filename=safe_title,
            save_yaml=True
        )
        
        if not rendering_result.success:
            self.logger.error(f"❌ Markdown rendering failed: {rendering_result.errors}")
            return PlanningResult(
                success=False,
                plan_data=plan_data,
                errors=rendering_result.errors
            )
        
        self.logger.info(f"✅ Plan rendered: {rendering_result.markdown_path}")
        if rendering_result.yaml_path:
            self.logger.info(f"✅ YAML saved: {rendering_result.yaml_path}")
        
        return PlanningResult(
            success=True,
            plan_data=plan_data,
            plan_path=rendering_result.yaml_path,
            markdown_path=rendering_result.markdown_path,
            validation_result=ValidationResult(valid=True)
        )
    
    def _create_error_result(
        self,
        error_message: str,
        validation_result: Optional[ValidationResult]
    ) -> OrchestratorResult:
        """
        Create error result.
        
        Args:
            error_message: Error message
            validation_result: Optional validation result
        
        Returns:
            OrchestratorResult with error status
        """
        self.end_time = datetime.now()
        execution_time = (self.end_time - self.start_time).total_seconds() if self.start_time else 0.0
        
        return OrchestratorResult(
            status=OrchestratorStatus.FAILED,
            success=False,
            message=error_message,
            errors=[error_message],
            warnings=validation_result.warnings if validation_result else [],
            execution_time_seconds=execution_time
        )
    
    def get_tdd_requirements(self) -> Dict[str, List[str]]:
        """
        Get TDD requirements for DoR/DoD compliance.
        
        Returns:
            Dictionary with 'dor' and 'dod' requirements
        """
        return {
            "dor": self._tdd_dor_requirements,
            "dod": self._tdd_dod_requirements
        }
    
    def is_schema_loaded(self) -> bool:
        """
        Check if schema is loaded.
        
        Returns:
            True if schema is loaded
        """
        return self.schema is not None
    
    def get_supported_plan_types(self) -> List[str]:
        """
        Get list of supported plan types.
        
        Returns:
            List of plan type names
        """
        return [t.value for t in PlanType]
    
    def get_complexity_levels(self) -> List[Dict[str, Any]]:
        """
        Get list of complexity levels.
        
        Returns:
            List of complexity level dictionaries
        """
        return [
            {"level": c.value, "name": c.name, "description": self._get_complexity_description(c)}
            for c in PlanComplexity
        ]
    
    def _get_complexity_description(self, complexity: PlanComplexity) -> str:
        """Get human-readable description of complexity level."""
        descriptions = {
            PlanComplexity.LOW: "Simple feature, skeleton plan with DoR/DoD only",
            PlanComplexity.MEDIUM: "Moderate feature, conditional phases with some detail",
            PlanComplexity.HIGH: "Complex feature, full incremental plan with all phases",
            PlanComplexity.CRITICAL: "Critical feature, full plan with security analysis"
        }
        return descriptions.get(complexity, "Unknown complexity level")
    
    # ========================================================================
    # Git Checkpoint Methods (Task 8.4 - Test Compliance)
    # ========================================================================
    
    def _create_checkpoint(self, phase_name: str, metadata: Dict[str, Any]) -> str:
        """
        Create git checkpoint for phase.
        
        Args:
            phase_name: Name of phase for checkpoint
            metadata: Additional checkpoint metadata
        
        Returns:
            Checkpoint ID if successful, empty string if failed
        """
        # Try git checkpoints first if available
        if self.git_checkpoint and self.git_checkpoint._is_git_repo():
            from .git_checkpoint_integration import CheckpointType
            
            checkpoint = self.git_checkpoint.create_checkpoint(
                checkpoint_type=CheckpointType.PHASE,
                phase_name=phase_name,
                message=f"Checkpoint: {phase_name} - {metadata.get('progress', 'N/A')}"
            )
            
            if checkpoint:
                # Store metadata in checkpoint for retrieval
                checkpoint.metadata = {"phase_name": phase_name, **metadata}
                return checkpoint.checkpoint_id
        
        # Fall back to in-memory checkpoints (for testing or non-git environments)
        self._checkpoint_counter += 1
        checkpoint_id = f"memory-checkpoint-{self._checkpoint_counter}"
        checkpoint_data = {
            "checkpoint_id": checkpoint_id,
            "phase_name": phase_name,
            "timestamp": datetime.now().isoformat(),
            **metadata
        }
        self._memory_checkpoints.append(checkpoint_data)
        return checkpoint_id
    
    def _create_checkpoint_with_validation(self, phase_name: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create checkpoint with validation before creation.
        
        Args:
            phase_name: Phase name
            metadata: Checkpoint metadata
        
        Returns:
            Result dictionary with validation status and checkpoint ID
        """
        # Validate metadata
        validation_errors = []
        if not phase_name:
            validation_errors.append("Phase name required")
        if not isinstance(metadata, dict):
            validation_errors.append("Metadata must be dictionary")
        
        if validation_errors:
            return {
                "success": False,
                "validation": False,
                "errors": validation_errors
            }
        
        # Create checkpoint
        checkpoint_id = self._create_checkpoint(phase_name, metadata)
        
        return {
            "success": bool(checkpoint_id),
            "validation": True,
            "checkpoint_id": checkpoint_id
        }
    
    def _create_git_checkpoint(self, phase_name: str, metadata: Dict[str, Any]) -> Optional[str]:
        """
        Create git checkpoint with git integration.
        
        Args:
            phase_name: Phase name
            metadata: Checkpoint metadata
        
        Returns:
            Checkpoint ID or None if failed
        """
        checkpoint_id = self._create_checkpoint(phase_name, metadata)
        return checkpoint_id if checkpoint_id else None
    
    def _get_checkpoint(self, checkpoint_id: str) -> Dict[str, Any]:
        """
        Get checkpoint data by ID.
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            Checkpoint data dictionary
        """
        # Check memory checkpoints first
        if hasattr(self, '_memory_checkpoints'):
            for checkpoint in self._memory_checkpoints:
                if checkpoint["checkpoint_id"] == checkpoint_id:
                    return checkpoint.copy()
        
        # Check git checkpoints
        if not self.git_checkpoint:
            return {}
        
        # Find checkpoint in history
        for checkpoint in self.git_checkpoint.checkpoints:
            if checkpoint.checkpoint_id == checkpoint_id:
                result = {
                    "checkpoint_id": checkpoint.checkpoint_id,
                    "phase_name": checkpoint.phase_name,
                    "commit_sha": checkpoint.commit_sha,
                    "branch_name": checkpoint.branch_name,
                    "message": checkpoint.message,
                    "timestamp": checkpoint.timestamp.isoformat(),
                    "files_changed": checkpoint.files_changed
                }
                # Add stored metadata if available
                if hasattr(checkpoint, 'metadata'):
                    result.update(checkpoint.metadata)
                return result
        
        return {}
    
    def _update_state(self, state_updates: Dict[str, Any]) -> None:
        """
        Update orchestrator state.
        
        Args:
            state_updates: State updates to apply
        """
        if not hasattr(self, '_internal_state'):
            self._internal_state = {}
        
        self._internal_state.update(state_updates)
    
    def _get_current_state(self) -> Dict[str, Any]:
        """
        Get current orchestrator state.
        
        Returns:
            Current state dictionary
        """
        if not hasattr(self, '_internal_state'):
            self._internal_state = {}
        
        return self._internal_state.copy()
    
    def _rollback_to_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Rollback to previous checkpoint.
        
        Args:
            checkpoint_id: Checkpoint to rollback to
        
        Returns:
            True if successful, False otherwise
        """
        # Find checkpoint to get metadata
        checkpoint_data = self._get_checkpoint(checkpoint_id)
        if not checkpoint_data:
            return False
        
        # For memory checkpoints, restore state directly
        if hasattr(self, '_memory_checkpoints') and checkpoint_id.startswith("memory-"):
            if hasattr(self, '_internal_state') and 'state' in checkpoint_data:
                self._internal_state['state'] = checkpoint_data['state']
            return True
        
        # For git checkpoints, use git restore
        if not self.git_checkpoint:
            return False
        
        # Restore git state
        success = self.git_checkpoint.restore_checkpoint(checkpoint_id)
        if success:
            # Restore orchestrator state from checkpoint metadata
            if hasattr(self, '_internal_state') and 'state' in checkpoint_data:
                self._internal_state['state'] = checkpoint_data['state']
            return True
        
        return False
    
    def _get_checkpoint_history(self) -> List[Dict[str, Any]]:
        """
        Get checkpoint history.
        
        Returns:
            List of checkpoint dictionaries
        """
        # Return memory checkpoints if available
        if hasattr(self, '_memory_checkpoints'):
            return [cp.copy() for cp in self._memory_checkpoints]
        
        # Return git checkpoints
        if not self.git_checkpoint:
            return []
        
        return [
            {
                "checkpoint_id": cp.checkpoint_id,
                "phase_name": cp.phase_name,
                "timestamp": cp.timestamp.isoformat(),
                "commit_sha": cp.commit_sha
            }
            for cp in self.git_checkpoint.checkpoints
        ]
    
    def _cleanup_old_checkpoints(self) -> None:
        """
        Cleanup old checkpoints beyond retention limit.
        """
        if not self.git_checkpoint:
            return
        
        retention_limit = getattr(self, 'checkpoint_retention_limit', 10)
        
        if len(self.git_checkpoint.checkpoints) > retention_limit:
            # Remove oldest checkpoints
            to_remove = len(self.git_checkpoint.checkpoints) - retention_limit
            self.git_checkpoint.checkpoints = self.git_checkpoint.checkpoints[to_remove:]
            self.git_checkpoint._persist_checkpoints()
    
    def _execute_phase_with_checkpoint(self, phase_name: str, phase_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute phase with automatic checkpoint creation.
        
        Args:
            phase_name: Name of phase to execute
            phase_config: Phase configuration
        
        Returns:
            Phase execution result
        """
        # Execute phase (placeholder - actual implementation would call phase executor)
        result = {
            "phase": phase_name,
            "status": "completed",
            "config": phase_config
        }
        
        # Create checkpoint after phase
        checkpoint_id = self._create_checkpoint(phase_name, {"phase_result": result})
        result["checkpoint_id"] = checkpoint_id
        
        return result
    
    def _get_created_checkpoints(self) -> List[str]:
        """
        Get list of created checkpoint IDs.
        
        Returns:
            List of checkpoint IDs
        """
        # Return memory checkpoint IDs if available
        if hasattr(self, '_memory_checkpoints'):
            return [cp["checkpoint_id"] for cp in self._memory_checkpoints]
        
        # Return git checkpoint IDs
        if not self.git_checkpoint:
            return []
        
        return [cp.checkpoint_id for cp in self.git_checkpoint.checkpoints]

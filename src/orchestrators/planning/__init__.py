"""
CORTEX 4.0 Planning System - Package Initialization

Purpose: Planning System 4.0 core package exports
Version: 4.0.0
Migrated: 2025-12-19

Package Structure (Week 8 MVP - Day 1-2 Complete):
- planning_orchestrator.py: Main orchestrator (800 LOC) ✅
- plan_validator.py: YAML schema validation (300 LOC) ✅
- plan_generator.py: Plan creation (400 LOC) ✅
- markdown_renderer.py: Markdown export (300 LOC) ✅
- plan_executor.py: Autonomous execution (500 LOC) - Day 3
- phase_manager_integration.py: PhaseManager wiring (300 LOC) - Day 3
- git_checkpoint_integration.py: Git checkpoints (200 LOC) - Day 3
- session_manager.py: Session restoration (200 LOC) - Day 3

Total Week 8 Day 1-2: 1,800 LOC complete (32% of 5,557 LOC total)
Total Week 8: 3,000 LOC planned (54% of 5,557 LOC total)
"""

# Core orchestrator
from .planning_orchestrator import (
    PlanningOrchestrator,
    PlanningPhase,
    PlanComplexity,
    PlanType,
    PlanMetadata,
    PlanPhaseData,
    PlanData,
    ValidationResult as PlanValidationResult,
    PlanningResult,
)

# Validator
from .plan_validator import (
    PlanValidator,
    ValidationResult,
    validate_plan,
    validate_plan_file,
)

# Generator
from .plan_generator import (
    PlanGenerator,
    ComplexityAnalyzer,
    GenerationResult,
    generate_plan,
)

# Renderer
from .markdown_renderer import (
    MarkdownRenderer,
    RenderingResult,
    render_plan,
    render_plan_from_file,
)

__all__ = [
    # Orchestrator
    "PlanningOrchestrator",
    "PlanningPhase",
    "PlanComplexity",
    "PlanType",
    "PlanMetadata",
    "PlanPhaseData",
    "PlanData",
    "PlanValidationResult",
    "PlanningResult",
    # Validator
    "PlanValidator",
    "ValidationResult",
    "validate_plan",
    "validate_plan_file",
    # Generator
    "PlanGenerator",
    "ComplexityAnalyzer",
    "GenerationResult",
    "generate_plan",
    # Renderer
    "MarkdownRenderer",
    "RenderingResult",
    "render_plan",
    "render_plan_from_file",
]

__version__ = "4.0.0"
__author__ = "CORTEX Development Team"
__migration_date__ = "2025-12-19"
__migration_phase__ = "Week 8 Day 1-2: Core Modules (1,800 LOC)"

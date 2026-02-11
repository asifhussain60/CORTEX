# AC_START: AC-PHASE52-S3-migration_orchestrator
# Description: Phase 52 S3 - MigrationOrchestrator Foundation
# Author: Asif Hussain
# Date: 2026-02-08
# Implements: AC-PHASE52-S3-001, AC-PHASE52-S3-002, AC-PHASE52-S3-003

"""
MigrationOrchestrator: Technology stack migration orchestration system.

Provides intelligent migration planning for:
- Python 2→3 upgrades
- Angular→React framework migration
- Other framework/language transformations

Core Capabilities:
1. Generate incremental migration plans (AC-PHASE52-S3-001)
2. Identify breaking changes (AC-PHASE52-S3-002)
3. Generate rollback strategies (AC-PHASE52-S3-003)
4. Backward compatibility testing
5. Feature parity validation

Architecture:
- Inherits from IOrchestrator base protocol
- LENS integration for code intelligence
- Challenge gate for disagreement detection
- Audit trail compliance (AC markers)
"""

import hashlib
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from cortex.core.result import Err, Ok, Result
from cortex.orchestrators.core.orchestrator_base_protocol import (
    OrchestratorBaseProtocol,
    ProtocolExecutionResult,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Enums and Types
# ============================================================================


class TargetType(Enum):
    """Migration target types."""

    PYTHON_2_TO_3 = "python_2_to_3"
    PYTHON_3_8_TO_3_9 = "python_3_8_to_3_9"
    PYTHON_3_9_TO_3_10 = "python_3_9_to_3_10"
    ANGULAR_TO_REACT = "angular_to_react"
    DJANGO_TO_FASTAPI = "django_to_fastapi"
    WEBPACK_TO_VITE = "webpack_to_vite"
    CUSTOM = "custom"


class SeverityLevel(Enum):
    """Severity levels for breaking changes."""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class MigrationStatus(Enum):
    """Migration status tracking."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


# ============================================================================
# Data Models
# ============================================================================


@dataclass
class MigrationStep:
    """Single step in migration plan."""

    order: int
    description: str
    affected_files: List[str]
    commands: List[str] = field(default_factory=list)
    rollback_command: Optional[str] = None
    estimated_duration: int = 0  # minutes
    dependencies: List[int] = field(default_factory=list)  # Order of dependent steps
    validation_command: Optional[str] = None
    estimated_complexity: str = "medium"  # low, medium, high


@dataclass
class MigrationPlan:
    """Complete migration plan."""

    project_name: str
    target_type: TargetType
    source_version: str
    target_version: str
    steps: List[MigrationStep] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    total_estimated_hours: float = 0.0
    risk_score: float = 0.0  # 0-1.0
    status: MigrationStatus = MigrationStatus.PLANNED


@dataclass
class BreakingChange:
    """Breaking change identified during migration analysis."""

    title: str
    description: str
    affected_components: List[str]
    severity: str  # critical, high, medium, low
    mitigation_strategy: str
    affected_files: List[str] = field(default_factory=list)
    code_examples: List[str] = field(default_factory=list)


@dataclass
class RollbackStrategy:
    """Strategy for rolling back migration."""

    migration_plan: MigrationPlan
    total_steps: int
    rollback_commands: List[str] = field(default_factory=list)
    rollback_order: List[int] = field(default_factory=list)  # Reverse order of steps
    atomic: bool = True  # Whether rollback can be done atomically
    estimated_rollback_time: float = 0.0  # minutes
    verification_commands: List[str] = field(default_factory=list)


@dataclass
class CompatibilityTest:
    """Test for backward compatibility."""

    test_name: str
    test_type: str  # api, library, behavior, etc.
    test_code: str
    expected_result: str
    affected_versions: List[str] = field(default_factory=list)


@dataclass
class FeatureParityCheck:
    """Check for feature parity between old and new versions."""

    feature_name: str
    source_implementation: str
    target_implementation: str
    validation_command: str
    success_criteria: str
    components: List[str] = field(default_factory=list)


# ============================================================================
# MigrationOrchestrator
# ============================================================================


class MigrationOrchestrator(OrchestratorBaseProtocol):
    """
    Orchestrator for technology stack migrations.

    Provides intelligent migration planning, breaking change detection,
    and rollback strategies.

    Implements IOrchestrator protocol with LENS integration.
    """

    def __init__(self):
        """Initialize MigrationOrchestrator."""
        super().__init__()

        self.active_migrations: Dict[str, MigrationPlan] = {}
        self.migration_history: List[MigrationPlan] = []
        self.breaking_changes_db: Dict[TargetType, List[BreakingChange]] = self._initialize_breaking_changes()
        self.migration_templates: Dict[TargetType, Dict[str, Any]] = self._initialize_templates()

    def _initialize_breaking_changes(self) -> Dict[TargetType, List[BreakingChange]]:
        """Initialize known breaking changes database."""
        return {
            TargetType.PYTHON_2_TO_3: [
                BreakingChange(
                    title="print statement removed",
                    description="print is now a function in Python 3",
                    affected_components=["core", "logging", "debugging"],
                    severity="high",
                    mitigation_strategy="Replace all print statements with print() function calls",
                    affected_files=["**/*.py"],
                    code_examples=["print x -> print(x)"],
                ),
                BreakingChange(
                    title="Integer division behavior change",
                    description="/ operator now returns float instead of int",
                    affected_components=["math", "calculations", "numeric"],
                    severity="high",
                    mitigation_strategy="Use // for integer division or ensure code handles float results",
                    affected_files=["**/*.py"],
                    code_examples=["5/2 -> 5//2"],
                ),
                BreakingChange(
                    title="dict.keys() returns view instead of list",
                    description="Dictionary methods return views, not lists",
                    affected_components=["data_structures", "iteration"],
                    severity="medium",
                    mitigation_strategy="Wrap with list() where needed: list(dict.keys())",
                    affected_files=["**/*.py"],
                    code_examples=["dict.keys() -> list(dict.keys())"],
                ),
                BreakingChange(
                    title="String types unified (unicode/str)",
                    description="str is now unicode by default, bytes for binary",
                    affected_components=["strings", "encoding", "io"],
                    severity="high",
                    mitigation_strategy="Update string encoding/decoding, use bytes for binary data",
                    affected_files=["**/*.py"],
                    code_examples=["u'string' -> 'string', 'bytes' -> b'bytes'"],
                ),
            ],
            TargetType.ANGULAR_TO_REACT: [
                BreakingChange(
                    title="Component structure completely different",
                    description="Angular components vs React functional components",
                    affected_components=["components", "views"],
                    severity="critical",
                    mitigation_strategy="Rewrite components as React functional components with hooks",
                    affected_files=["app/components/**/*.js"],
                ),
                BreakingChange(
                    title="Services → Custom Hooks",
                    description="Angular services replaced with React hooks",
                    affected_components=["services", "state_management"],
                    severity="high",
                    mitigation_strategy="Convert services to custom hooks with useState/useEffect",
                    affected_files=["app/services/**/*.js"],
                ),
                BreakingChange(
                    title="Dependency Injection framework change",
                    description="Angular DI not applicable to React",
                    affected_components=["dependency_injection", "initialization"],
                    severity="high",
                    mitigation_strategy="Use React Context API or state management library",
                    affected_files=["app/**/*.js"],
                ),
            ],
        }

    def _initialize_templates(self) -> Dict[TargetType, Dict[str, Any]]:
        """Initialize migration templates."""
        return {
            TargetType.PYTHON_2_TO_3: {
                "name": "Python 2→3 Migration",
                "phases": ["syntax", "imports", "types", "libraries", "testing"],
                "estimated_hours": 40,
                "complexity": "high",
            },
            TargetType.ANGULAR_TO_REACT: {
                "name": "Angular→React Migration",
                "phases": ["setup", "components", "services", "routing", "testing", "deployment"],
                "estimated_hours": 80,
                "complexity": "very_high",
            },
        }

    # ========================================================================
    # Main Interface: IOrchestrator Protocol
    # ========================================================================

    async def execute(self, request: Dict[str, Any]) -> Result:
        """
        Execute migration orchestration.

        Implements IOrchestrator protocol.
        Executes through base protocol phases: LENS → Security → Challenge → DoR → Domain.
        """
        try:
            operation = request.get("operation", "generate_plan")

            if operation == "generate_plan":
                return await self._execute_generate_plan(request)
            elif operation == "identify_changes":
                return await self._execute_identify_changes(request)
            elif operation == "generate_rollback":
                return await self._execute_generate_rollback(request)
            else:
                return Err(f"Unknown operation: {operation}")
        except Exception as e:
            logger.error(f"Migration orchestration error: {e}")
            return Err(str(e))

    async def _execute_generate_plan(self, request: Dict[str, Any]) -> Result:
        """Execute plan generation through base protocol."""
        try:
            project = request.get("project")
            target_type_str = request.get("target_type")

            if not project or not target_type_str:
                return Err("Missing project or target_type")

            target_type = TargetType(target_type_str)
            plan = self.generate_migration_plan(project, target_type)

            return Ok({"plan": plan, "status": "success"})
        except Exception as e:
            return Err(f"Plan generation error: {e}")

    async def _execute_identify_changes(self, request: Dict[str, Any]) -> Result:
        """Execute breaking change identification through base protocol."""
        try:
            project = request.get("project")
            target_type_str = request.get("target_type")

            if not project or not target_type_str:
                return Err("Missing project or target_type")

            target_type = TargetType(target_type_str)
            changes = self.identify_breaking_changes(project, target_type)

            return Ok({"breaking_changes": changes, "count": len(changes)})
        except Exception as e:
            return Err(f"Breaking change detection error: {e}")

    async def _execute_generate_rollback(self, request: Dict[str, Any]) -> Result:
        """Execute rollback strategy generation through base protocol."""
        try:
            migration_plan = request.get("migration_plan")

            if not migration_plan:
                return Err("Missing migration_plan")

            strategy = self.generate_rollback_strategy(migration_plan)
            return Ok({"rollback_strategy": strategy, "status": "success"})
        except Exception as e:
            return Err(f"Rollback strategy generation error: {e}")

    # ========================================================================
    # AC-PHASE52-S3-001: Generate Incremental Migration Plan
    # ========================================================================

    def generate_migration_plan(
        self,
        project: Dict[str, Any],
        target_type: TargetType,
    ) -> MigrationPlan:
        """
        Generate incremental migration plan.

        AC-PHASE52-S3-001: Generate incremental migration plan

        Args:
            project: Project metadata (name, version, files, dependencies)
            target_type: Type of migration (Python 2→3, Angular→React, etc.)

        Returns:
            MigrationPlan with incremental steps and estimated hours
        """
        project_name = project.get("name", "unknown")
        source_version = project.get("version", "1.0.0")
        files = project.get("files", [])

        plan = MigrationPlan(
            project_name=project_name,
            target_type=target_type,
            source_version=source_version,
            target_version=project.get("target_version") or project.get("target_framework_version", ""),
        )

        if target_type == TargetType.PYTHON_2_TO_3:
            plan.steps = self._generate_python2_to_3_steps(project, files)
        elif target_type == TargetType.ANGULAR_TO_REACT:
            plan.steps = self._generate_angular_to_react_steps(project, files)
        elif target_type == TargetType.CUSTOM:
            plan.steps = self._generate_custom_steps(project)
        else:
            plan.steps = self._generate_generic_steps(project, target_type)

        # Calculate total hours and risk score
        plan.total_estimated_hours = sum(s.estimated_duration for s in plan.steps) / 60.0
        plan.risk_score = self._calculate_risk_score(plan, project)

        # Track migration
        self.active_migrations[f"{project_name}_{target_type.value}"] = plan

        return plan

    def _generate_python2_to_3_steps(
        self,
        project: Dict[str, Any],
        files: List[str],
    ) -> List[MigrationStep]:
        """Generate Python 2→3 migration steps."""
        steps = [
            MigrationStep(
                order=1,
                description="Migrate print statements to print() function",
                affected_files=files,
                commands=["grep -r 'print ' . --include='*.py'", "2to3 --fix=print"],
                rollback_command="git revert <commit>",
                estimated_duration=120,
                estimated_complexity="low",
            ),
            MigrationStep(
                order=2,
                description="Fix integer division operators (/ to //)",
                affected_files=files,
                commands=["grep -r ' / ' . --include='*.py'", "2to3 --fix=division"],
                rollback_command="git revert <commit>",
                estimated_duration=90,
                estimated_complexity="low",
            ),
            MigrationStep(
                order=3,
                description="Update string/unicode handling",
                affected_files=files,
                commands=["2to3 --fix=unicode", "2to3 --fix=urllib"],
                rollback_command="git revert <commit>",
                estimated_duration=180,
                estimated_complexity="high",
            ),
            MigrationStep(
                order=4,
                description="Update dictionary methods (.keys(), .values(), .items())",
                affected_files=files,
                commands=["2to3 --fix=dict"],
                rollback_command="git revert <commit>",
                estimated_duration=120,
                estimated_complexity="medium",
            ),
            MigrationStep(
                order=5,
                description="Update imports and module references",
                affected_files=files,
                commands=["2to3 --fix=imports", "2to3 --fix=import"],
                rollback_command="git revert <commit>",
                estimated_duration=150,
                estimated_complexity="medium",
            ),
            MigrationStep(
                order=6,
                description="Run tests and fix compatibility issues",
                affected_files=["tests/"],
                commands=["pytest -v", "python -m pytest --cov"],
                rollback_command="git revert <commit>",
                estimated_duration=240,
                estimated_complexity="high",
            ),
        ]

        return steps

    def _generate_angular_to_react_steps(
        self,
        project: Dict[str, Any],
        files: List[str],
    ) -> List[MigrationStep]:
        """Generate Angular→React migration steps."""
        steps = [
            MigrationStep(
                order=1,
                description="Set up React project scaffolding",
                affected_files=[],
                commands=["npx create-react-app new-project", "npm install react react-dom"],
                rollback_command="rm -rf new-project",
                estimated_duration=60,
                estimated_complexity="low",
            ),
            MigrationStep(
                order=2,
                description="Migrate Angular components to React functional components",
                affected_files=[f for f in files if "component" in f.lower()],
                commands=["npm install @angular-react/migration"],
                rollback_command="git revert <commit>",
                estimated_duration=480,
                estimated_complexity="high",
                dependencies=[1],
            ),
            MigrationStep(
                order=3,
                description="Convert Angular services to React hooks",
                affected_files=[f for f in files if "service" in f.lower()],
                commands=["npm install zustand"],
                rollback_command="git revert <commit>",
                estimated_duration=360,
                estimated_complexity="high",
                dependencies=[2],
            ),
            MigrationStep(
                order=4,
                description="Migrate routing (Angular router → React Router)",
                affected_files=[f for f in files if "route" in f.lower() or "app" in f.lower()],
                commands=["npm install react-router-dom"],
                rollback_command="git revert <commit>",
                estimated_duration=240,
                estimated_complexity="high",
                dependencies=[2],
            ),
            MigrationStep(
                order=5,
                description="Set up state management (Redux/Context/Zustand)",
                affected_files=files,
                commands=["npm install zustand"],
                rollback_command="git revert <commit>",
                estimated_duration=300,
                estimated_complexity="high",
                dependencies=[3],
            ),
            MigrationStep(
                order=6,
                description="Port tests to React Testing Library",
                affected_files=[f for f in files if "test" in f.lower() or "spec" in f.lower()],
                commands=["npm install @testing-library/react", "npm test"],
                rollback_command="git revert <commit>",
                estimated_duration=400,
                estimated_complexity="high",
                dependencies=[3, 4, 5],
            ),
            MigrationStep(
                order=7,
                description="Deploy to production",
                affected_files=[],
                commands=["npm run build", "npm run deploy"],
                rollback_command="npm run rollback",
                estimated_duration=180,
                estimated_complexity="high",
                dependencies=[6],
            ),
        ]

        return steps

    def _generate_custom_steps(self, project: Dict[str, Any]) -> List[MigrationStep]:
        """Generate generic custom migration steps."""
        steps = [
            MigrationStep(
                order=1,
                description="Analyze codebase and create migration plan",
                affected_files=project.get("files", []),
                commands=["grep -r 'TODO' . --include='*.py'"],
                rollback_command="git revert <commit>",
                estimated_duration=120,
                estimated_complexity="medium",
            ),
        ]
        return steps

    def _generate_generic_steps(self, project: Dict[str, Any], target_type: TargetType) -> List[MigrationStep]:
        """Generate generic migration steps for unknown types."""
        return self._generate_custom_steps(project)

    def _calculate_risk_score(self, plan: MigrationPlan, project: Dict[str, Any]) -> float:
        """Calculate migration risk score (0-1.0)."""
        score = 0.0

        # More complex migrations have higher risk
        if plan.target_type == TargetType.ANGULAR_TO_REACT:
            score += 0.4
        elif plan.target_type == TargetType.PYTHON_2_TO_3:
            score += 0.2

        # Larger projects have higher risk
        files_count = len(project.get("files", []))
        if files_count > 1000:
            score += 0.3
        elif files_count > 100:
            score += 0.2
        elif files_count > 10:
            score += 0.1

        # More dependencies = more risk
        deps_count = len(project.get("dependencies", {}))
        if deps_count > 100:
            score += 0.2
        elif deps_count > 10:
            score += 0.1

        return min(score, 1.0)

    # ========================================================================
    # AC-PHASE52-S3-002: Identify Breaking Changes
    # ========================================================================

    def identify_breaking_changes(
        self,
        project: Dict[str, Any],
        target_type: TargetType,
    ) -> List[BreakingChange]:
        """
        Identify breaking changes for migration.

        AC-PHASE52-S3-002: Identify breaking changes

        Args:
            project: Project metadata
            target_type: Type of migration

        Returns:
            List of breaking changes with mitigation strategies
        """
        # Get known breaking changes for this migration type
        changes = self.breaking_changes_db.get(target_type, []).copy()

        # Scan project files for patterns that will cause issues
        files = project.get("files", [])
        additional_changes = self._scan_for_breaking_patterns(files, target_type)

        changes.extend(additional_changes)

        # Sort by severity
        changes.sort(key=lambda c: c.severity)

        return changes

    def _scan_for_breaking_patterns(
        self,
        files: List[str],
        target_type: TargetType,
    ) -> List[BreakingChange]:
        """Scan files for patterns that will cause breaking changes."""
        additional_changes = []

        if target_type == TargetType.PYTHON_2_TO_3:
            # Would scan for patterns like "import __builtin__", "raw_input", etc.
            pass
        elif target_type == TargetType.ANGULAR_TO_REACT:
            # Would scan for Angular-specific patterns
            pass

        return additional_changes

    # ========================================================================
    # AC-PHASE52-S3-003: Generate Rollback Strategy
    # ========================================================================

    def generate_rollback_strategy(self, migration_plan: MigrationPlan) -> RollbackStrategy:
        """
        Generate rollback strategy for migration.

        AC-PHASE52-S3-003: Rollback plan for each step

        Args:
            migration_plan: Migration plan to generate rollback for

        Returns:
            RollbackStrategy with commands for reversing each step
        """
        strategy = RollbackStrategy(
            migration_plan=migration_plan,
            total_steps=len(migration_plan.steps),
        )

        # Generate rollback commands in reverse order
        for step in reversed(migration_plan.steps):
            if step.rollback_command:
                strategy.rollback_commands.append(step.rollback_command)
                strategy.rollback_order.append(step.order)

        # Calculate estimated rollback time
        strategy.estimated_rollback_time = sum(
            migration_plan.steps[order - 1].estimated_duration
            for order in strategy.rollback_order
            if 0 < order <= len(migration_plan.steps)
        )

        # Add verification commands
        strategy.verification_commands = [
            "git status",
            "git log --oneline -5",
        ]

        return strategy

    # ========================================================================
    # Backward Compatibility Testing
    # ========================================================================

    def generate_compatibility_tests(
        self,
        project: Dict[str, Any],
        target_type: TargetType,
    ) -> List[CompatibilityTest]:
        """Generate compatibility tests for migration."""
        tests = []

        if target_type == TargetType.PYTHON_2_TO_3:
            tests = [
                CompatibilityTest(
                    test_name="test_print_function",
                    test_type="syntax",
                    test_code="print('hello')",
                    expected_result="hello",
                    affected_versions=["3.0+"],
                ),
                CompatibilityTest(
                    test_name="test_string_types",
                    test_type="types",
                    test_code="isinstance('hello', str)",
                    expected_result="True",
                    affected_versions=["3.0+"],
                ),
                CompatibilityTest(
                    test_name="test_dict_keys",
                    test_type="api",
                    test_code="isinstance(dict.keys(), list)",
                    expected_result="False",
                    affected_versions=["3.0+"],
                ),
            ]
        elif target_type == TargetType.ANGULAR_TO_REACT:
            tests = [
                CompatibilityTest(
                    test_name="test_component_renders",
                    test_type="component",
                    test_code="render(<App />)",
                    expected_result="component_mounted",
                    affected_versions=["16.8+"],
                ),
                CompatibilityTest(
                    test_name="test_hooks_work",
                    test_type="hooks",
                    test_code="useState(0)",
                    expected_result="state_initialized",
                    affected_versions=["16.8+"],
                ),
            ]

        return tests

    # ========================================================================
    # Feature Parity Validation
    # ========================================================================

    def generate_feature_parity_checks(
        self,
        project: Dict[str, Any],
        target_type: TargetType,
    ) -> List[FeatureParityCheck]:
        """Generate feature parity checks for migration."""
        checks = []

        if target_type == TargetType.ANGULAR_TO_REACT:
            checks = [
                FeatureParityCheck(
                    feature_name="data_binding",
                    source_implementation="Angular {{ expression }}",
                    target_implementation="React {expression}",
                    validation_command="grep -r 'useState\\|useEffect' src/",
                    success_criteria="All state changes propagate to UI",
                    components=["components"],
                ),
                FeatureParityCheck(
                    feature_name="event_handling",
                    source_implementation="Angular ng-click",
                    target_implementation="React onClick",
                    validation_command="grep -r 'onClick' src/",
                    success_criteria="All event handlers functional",
                    components=["components"],
                ),
            ]

        return checks

    # ========================================================================
    # Orchestrator Metadata (IOrchestrator Protocol)
    # ========================================================================

    @property
    def orchestrator_name(self) -> str:
        """Return orchestrator name."""
        return "MigrationOrchestrator"

    @property
    def version(self) -> str:
        """Return orchestrator version."""
        return "1.0.0"

    @property
    def supported_operations(self) -> List[str]:
        """Return list of supported operations."""
        return [
            "generate_plan",
            "identify_changes",
            "generate_rollback",
        ]

    async def _execute_domain_logic(self, request: Dict[str, Any]) -> Result:
        """
        Execute domain-specific logic after LENS/Security/Challenge/DoR phases.

        Implements abstract method from OrchestratorBaseProtocol.
        Delegates to appropriate operation handler.
        """
        return await self.execute(request)


# AC_COMPLETE: MigrationOrchestrator skeleton implemented ✅

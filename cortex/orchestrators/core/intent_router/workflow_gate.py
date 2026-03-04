"""
Complexity-Gated Workflow Router - Core Implementation

Routes tasks to workflow templates or direct orchestrators based on complexity scoring.
Prevents golden hammer anti-pattern through intelligent threshold-based routing.

Authority: WORKFLOW-COMPLEXITY-GATE-001
Date: 2026-02-17
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List


class ComplexityThreshold(Enum):
    """Complexity thresholds aligned with CONF-GATE (CORE-046)."""
    TRIVIAL = 0.15      # Direct orchestrator (auto-approve)
    SIMPLE = 0.35       # Direct orchestrator (minimal validation)
    MODERATE = 0.60     # Workflow template (structured approach)
    COMPLEX = 0.75      # Workflow template (mandatory gates)


class RoutingStrategy(Enum):  # CORE-035-scoped — domain-specific variant
    """Routing strategies for task execution."""
    DIRECT_ORCHESTRATOR = "direct_orchestrator"
    WORKFLOW_TEMPLATE = "workflow_template"


@dataclass
class Intent:  # CORE-035-scoped — domain-specific variant
    """Parsed user intent for complexity analysis."""
    operation_type: str
    target_files: List[str] = None  # type: ignore[assignment]
    dependencies: List[str] = None  # type: ignore[assignment]
    risk_level: str = "LOW"
    metadata: Dict[str, Any] = None  # type: ignore[assignment]
    # Phase 92: intent classification context (optional, from IntentClassifier)
    intent_type: Optional[Any] = None
    confidence: float = 0.0

    def __post_init__(self) -> None:
        """Initialise mutable defaults."""
        if self.target_files is None:
            self.target_files = []
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RoutingDecision:  # CORE-035-scoped — domain-specific routing decision model
    """Decision output from complexity router."""
    route: RoutingStrategy
    complexity: float
    rationale: str
    orchestrator: Optional[str] = None
    template_id: Optional[str] = None
    requires_confirmation: bool = False
    governance_gate: Optional[str] = None


class WorkflowComplexityRouter:
    """
    Routes tasks to workflow templates or direct orchestrators based on complexity.

    Scoring dimensions (aligned with CONF-GATE-001):
    - File count (30%): min(files/10, 1.0)
    - Operation type (40%): Predefined scores
    - Dependencies (20%): min(deps/5, 1.0)
    - Risk level (10%): {LOW:0.2, MEDIUM:0.5, HIGH:0.8, CRITICAL:1.0}

    Authority: WORKFLOW-COMPLEXITY-GATE-001
    """

    # Thresholds aligned with CONF-GATE rules (CORE-046)
    # Phase 122: MODERATE lowered from 0.60 → 0.40 so meaningful multi-file operations
    # (5+ file implement/refactor) reach the workflow template path. Analysis:
    #   1-file fix (LOW):             score ≈ 0.17 → DIRECT_ORCHESTRATOR ✅
    #   3-file implement (MEDIUM):    score ≈ 0.34 → DIRECT_ORCHESTRATOR ✅
    #   5-file implement (MEDIUM):    score ≈ 0.40 → WORKFLOW_TEMPLATE   ✅
    #   3-file refactor+2deps (MED):  score ≈ 0.46 → WORKFLOW_TEMPLATE   ✅
    # See cortex-registry/_cortex-master/phases/phase-122-workflow-composer-activation.yaml
    TRIVIAL_THRESHOLD = ComplexityThreshold.TRIVIAL.value
    SIMPLE_THRESHOLD = ComplexityThreshold.SIMPLE.value
    MODERATE_THRESHOLD = 0.39  # Phase 122: was ComplexityThreshold.MODERATE.value (0.60)
    COMPLEX_THRESHOLD = ComplexityThreshold.COMPLEX.value

    # Operation type complexity scores (40% weight)
    # Phase 122: "implement" added explicitly (was falling back to 0.5 undocumented default)
    OPERATION_SCORES = {
        "implement": 0.5,   # Phase 122: explicit — TDD cycle, multi-file, meaningful scope
        "create": 0.4,
        "refactor": 0.6,
        "migrate": 0.8,
        "test": 0.5,
        "security": 0.7,
        "document": 0.2,
        "fix": 0.3,
        "update": 0.2,
        "delete": 0.4,
        "deploy": 0.7,
    }

    # Risk level scores (10% weight)
    RISK_SCORES = {
        "LOW": 0.2,
        "MEDIUM": 0.5,
        "HIGH": 0.8,
        "CRITICAL": 1.0,
    }

    def score_task_complexity(self, intent: Intent) -> float:
        """
        Score task complexity (0.0-1.0) based on dimensions.

        Args:
            intent: Parsed user intent with task details

        Returns:
            Complexity score (0.0 = trivial, 1.0 = highly complex)
        """
        score = 0.0

        # Dimension 1: File count (30% weight)
        file_count = len(intent.target_files)
        file_score = min(file_count / 10, 1.0) * 0.30

        # Dimension 2: Operation type (40% weight)
        operation_score = self.OPERATION_SCORES.get(
            intent.operation_type.lower(), 0.5
        ) * 0.40

        # Dimension 3: Dependency depth (20% weight)
        dep_count = len(intent.dependencies)
        dep_score = min(dep_count / 5, 1.0) * 0.20

        # Dimension 4: Risk level (10% weight)
        risk_score = self.RISK_SCORES.get(intent.risk_level.upper(), 0.5) * 0.10

        # Total score
        score = file_score + operation_score + dep_score + risk_score

        return min(score, 1.0)

    def route(self, intent: Intent) -> RoutingDecision:
        """Route an intent to the appropriate orchestrator based on complexity scoring.

        Evaluates file impact, operation type, dependency footprint, and risk level
        to produce a ``RoutingDecision`` with the selected ``RoutingStrategy``.

        Args:
            intent: The ``Intent`` object to route.

        Returns:
            A ``RoutingDecision`` describing the chosen strategy, orchestrator,
            complexity score, rationale, and whether confirmation is required.
        """
        complexity = self.score_task_complexity(intent)

        if complexity < self.TRIVIAL_THRESHOLD:
            return RoutingDecision(
                route=RoutingStrategy.DIRECT_ORCHESTRATOR,
                complexity=complexity,
                rationale="Trivial operation, no workflow overhead",
                orchestrator=self._select_orchestrator(intent),
                requires_confirmation=False
            )

        elif complexity < self.SIMPLE_THRESHOLD:
            return RoutingDecision(
                route=RoutingStrategy.DIRECT_ORCHESTRATOR,
                complexity=complexity,
                rationale="Simple operation, direct orchestration sufficient",
                orchestrator=self._select_orchestrator(intent),
                requires_confirmation=False
            )

        elif complexity < self.MODERATE_THRESHOLD:
            return RoutingDecision(
                route=RoutingStrategy.WORKFLOW_TEMPLATE,
                complexity=complexity,
                rationale="Moderate complexity, structured workflow recommended",
                template_id=self._select_template(intent),
                requires_confirmation=True
            )

        else:  # >= COMPLEX_THRESHOLD
            return RoutingDecision(
                route=RoutingStrategy.WORKFLOW_TEMPLATE,
                complexity=complexity,
                rationale="High complexity, mandatory workflow template",
                template_id=self._select_template(intent),
                requires_confirmation=True,
                governance_gate="MANDATORY"
            )

    def evaluate(self, intent: Intent) -> RoutingDecision:
        """Evaluate intent and return a RoutingDecision.

        Phase 92: Public alias for ``route()`` that always populates the
        ``orchestrator`` field — even when a workflow template is selected —
        so callers can reliably check ``result.orchestrator`` for visual
        engagement breadcrumbs.

        Args:
            intent: Parsed user intent with operation details.

        Returns:
            RoutingDecision with ``orchestrator`` always set.
        """
        decision = self.route(intent)
        # Ensure orchestrator is always resolved for breadcrumb rendering
        if decision.orchestrator is None:
            decision = RoutingDecision(
                route=decision.route,
                complexity=decision.complexity,
                rationale=decision.rationale,
                orchestrator=self._select_orchestrator(intent),
                template_id=decision.template_id,
                requires_confirmation=decision.requires_confirmation,
                governance_gate=decision.governance_gate,
            )
        return decision

    def _select_orchestrator(self, intent: Intent) -> str:
        """Select appropriate orchestrator for direct execution.

        Maps all 18 CORTEX execution modes to their canonical orchestrators.
        Unknown operations fallback to InteractionOrchestrator (LENS comprehension).

        Args:
            intent: Parsed user intent with operation details.

        Returns:
            Orchestrator class name string.
        """
        operation_type = intent.operation_type.lower()

        orchestrator_map = {
            # Core operational (IMPLEMENT, FIX, REFACTOR)
            "fix": "RefactoringOrchestrator",
            "update": "RefactoringOrchestrator",
            "refactor": "RefactoringOrchestrator",
            "create": "TDDOrchestrator",
            "implement": "TDDOrchestrator",
            "test": "TDDOrchestrator",
            "golden_test": "TDDOrchestrator",
            # Analysis & Investigation
            "analyze": "AnalysisOrchestrator",
            "investigate": "InvestigationOrchestrator",
            "rca": "InvestigationOrchestrator",
            "audit": "HealthOrchestrator",
            "health": "HealthOrchestrator",
            # Planning & Design
            "design": "ArchitectOrchestrator",
            "plan": "PlanningOrchestrator",
            # Content & Knowledge
            "document": "DocumentationOrchestrator",
            "digest": "DigestSessionOrchestrator",
            "rephrase": "RequestRephraseOrchestrator",
            # Support & Tooling
            "security": "SecurityOrchestrator",
            "deploy": "DeploymentOrchestrator",
            "vacuum": "VacuumOrchestrator",
            "debug": "DebuggerOrchestrator",
            # Git & Sync
            "sync": "GitOrchestrator",
            # Intelligence & Training
            "train": "TrainerOrchestrator",
            "onboard": "RepositoryOnboardingOrchestrator",
            # Holistic
            "totalrecall": "MasterOrchestrator",
            # GAP-89-COMPOSE: Workflow Composer — convergence loops + full toolchain
            "workflow_compose": "WorkflowComposer",
        }

        return orchestrator_map.get(operation_type, "InteractionOrchestrator")

    # Technology-qualified template map — (operation, technology) → template_id
    # Phase 89-a: Routes to existing YAML templates in cortex-registry/workflows/templates/
    TECHNOLOGY_TEMPLATE_MAP: Dict[tuple, str] = {
        # Frontend templates
        ("refactor", "html"): "frontend/html-refactor-validation",
        ("refactor", "css"): "frontend/css-extraction-workflow",
        ("refactor", "typescript"): "frontend/typescript-refactor-workflow",
        ("create", "css"): "frontend/css-zero-inline-workflow",
        # Backend templates
        ("refactor", "csharp"): "backend/csharp-refactor-workflow",
        ("security", "csharp"): "backend/csharp-security-workflow",
    }

    # File extension → technology mapping for auto-detection
    EXTENSION_TECHNOLOGY_MAP: Dict[str, str] = {
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "css",
        ".sass": "css",
        ".less": "css",
        ".cs": "csharp",
        ".csx": "csharp",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".py": "python",
        ".pyw": "python",
    }

    def detect_technology(self, intent: Intent) -> Optional[str]:
        """Detect technology from intent metadata or file extensions.

        Priority:
        1. Explicit ``metadata["technology"]`` — always wins.
        2. Majority file-extension inference — if >50% of files share a technology.

        Args:
            intent: Parsed user intent with file list and metadata.

        Returns:
            Technology string (e.g. ``"html"``, ``"csharp"``) or ``None``.
        """
        # Priority 1: explicit metadata
        explicit = intent.metadata.get("technology")
        if explicit:
            return str(explicit).lower()

        # Priority 2: file extension majority vote
        if not intent.target_files:
            return None

        tech_counts: Dict[str, int] = {}
        for filepath in intent.target_files:
            ext = ""
            # Extract extension (last dot-segment)
            dot_idx = filepath.rfind(".")
            if dot_idx != -1:
                ext = filepath[dot_idx:].lower()
            tech = self.EXTENSION_TECHNOLOGY_MAP.get(ext)
            if tech:
                tech_counts[tech] = tech_counts.get(tech, 0) + 1

        if not tech_counts:
            return None

        # Majority: the dominant technology must have > 50% of files
        total = len(intent.target_files)
        best_tech = max(tech_counts, key=lambda k: tech_counts[k])
        if tech_counts[best_tech] > total / 2:
            return best_tech

        return None

    def _select_template(self, intent: Intent) -> str:
        """Select appropriate workflow template.

        Uses technology-qualified mapping first (Phase 89-a), then generic
        static mapping, then falls back to TemplateComposer for dynamic
        composition from validated primitives (Phase 55).

        Args:
            intent: Parsed user intent with operation details.

        Returns:
            Template ID string (technology-specific, static, or composed).
        """
        operation_type = intent.operation_type.lower()

        # Phase 89-a: Technology-qualified template selection (fast path)
        technology = self.detect_technology(intent)
        if technology:
            tech_key = (operation_type, technology)
            if tech_key in self.TECHNOLOGY_TEMPLATE_MAP:
                return self.TECHNOLOGY_TEMPLATE_MAP[tech_key]

        # Generic static mapping (backward compatible)
        template_map = {
            "create": "tdd/feature-implementation",
            "test": "tdd/feature-implementation",
            "refactor": "quality/refactoring",
            "migrate": "migration/legacy-modernization",
            "security": "security/audit-remediation",
            "deploy": "deployment/production-release",
            # GAP-89-COMPOSE: Workflow Composer routes to dynamic composition
            # via TemplateComposer — uses convergence loops + full CORTEX toolchain
            "workflow_compose": "composites/dynamic-workflow-composition",
        }

        # Static match — fast path
        if operation_type in template_map:
            return template_map[operation_type]

        # Phase 55: Dynamic composition from primitives (fallback)
        try:
            from cortex.orchestrators.workflow.template_composer import TemplateComposer
            from pathlib import Path

            primitives_dir = Path("cortex-registry/workflows/templates/primitives")
            composites_dir = Path("cortex-registry/workflows/templates/composites")

            if primitives_dir.exists():
                composer = TemplateComposer(
                    primitives_dir=primitives_dir,
                    composites_dir=composites_dir,
                )
                description = intent.metadata.get("description", operation_type)
                composed = composer.compose(
                    operation_type=operation_type,
                    description=str(description),
                )
                if composed is not None:
                    composer.persist(composed)
                    return composed["id"]
        except Exception:
            pass  # Non-blocking — fall through to default

        # Ultimate fallback
        return "tdd/feature-implementation"

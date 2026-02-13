"""
Test Demand Generator - Intelligence Layer for Automatic Test Creation

Analyzes orchestrator specifications and generates intelligent test demands
without manual intervention. Forms foundation of Test Quality Wave v2.

Authority: PHASE-51-S4-TEST-INTELLIGENCE | CORE-008 (TDD-First)
AC-ID: AC-PHASE51-S4-DEMAND-GEN-001
Purpose: Transform test creation from manual to intelligent automation

Components:
1. DemandAnalyzer - Reads orchestrator specs, identifies test scenarios
2. DemandRegistry - Stores and manages test demands (YAML-backed)
3. DemandValidator - Validates demands for completeness and realism
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

logger = logging.getLogger(__name__)


class DemandCategory(str, Enum):
    """Test demand categories (what MUST be tested)."""
    SILENT_OPERATION = "silent_operation"  # e.g., YAML created silently
    CONTEXT_SYNTHESIS = "context_synthesis"  # e.g., LENS merging
    LOOP_INTELLIGENCE = "loop_intelligence"  # e.g., RGR loop termination
    GATE_ENFORCEMENT = "gate_enforcement"  # e.g., DoD blocking approval
    TEMPLATE_QUALITY = "template_quality"  # e.g., response formatting
    AUDIT_COMPLIANCE = "audit_compliance"  # e.g., audit trail logging
    ERROR_RECOVERY = "error_recovery"  # e.g., graceful failure handling
    INTEGRATION_COUPLING = "integration_coupling"  # e.g., orchestrator events
    STATE_PERSISTENCE = "state_persistence"  # e.g., YAML file consistency
    PERFORMANCE_BOUNDS = "performance_bounds"  # e.g., max loop iterations


class ValidationType(str, Enum):
    """How test validates the demand."""
    FILE_SYSTEM = "file_system"  # Check files exist/created
    AUDIT_LOG = "audit_log"  # Verify audit trail entries
    OUTPUT_STRUCTURE = "output_structure"  # Validate response format
    METRIC_BOUNDS = "metric_bounds"  # Check counters, timers
    STATE_CONSISTENCY = "state_consistency"  # Verify YAML/DB state
    EVENT_EMISSION = "event_emission"  # Check events published
    EXECUTION_PATH = "execution_path"  # Verify code path taken


@dataclass
class TestDemand:
    """A test demand - what a test MUST validate."""
    
    id: str
    orchestrator: str
    category: DemandCategory
    title: str
    description: str
    
    # What to test
    scenario: str  # Real-world scenario (e.g., "user says 'implement login'")
    expected_behavior: str  # What MUST happen
    
    # How to validate
    validation_type: ValidationType
    validation_rules: Dict[str, Any] = field(default_factory=dict)
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)  # Other demand IDs
    blocks: List[str] = field(default_factory=list)  # Which demands this blocks
    
    # Metadata
    complexity: str = "medium"  # simple|medium|complex
    priority: int = 1  # 1=critical, 5=optional
    audit_requirements: List[str] = field(default_factory=list)  # AC markers needed
    
    # Quality metrics
    coverage_percentage: float = 0.0
    is_golden_path: bool = False
    estimated_test_lines: int = 0
    
    created_at: str = field(default_factory=lambda: "2026-02-13")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TestDemand":
        """Load from dictionary (registry YAML)."""
        data["category"] = DemandCategory(data.get("category", "silent_operation"))
        data["validation_type"] = ValidationType(data.get("validation_type", "audit_log"))
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML storage."""
        result = asdict(self)
        result["category"] = self.category.value
        result["validation_type"] = self.validation_type.value
        return result


@dataclass
class DemandAnalysisResult:
    """Result of analyzing an orchestrator for test demands."""
    orchestrator_name: str
    demands: List[TestDemand] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)  # Missing coverage areas
    
    total_lines_of_test_code: int = 0
    estimated_test_count: int = 0
    coverage_percentage: float = 0.0
    
    analysis_notes: str = ""
    timestamp: str = field(default_factory=lambda: "2026-02-13T00:00:00Z")

    def to_yaml(self) -> str:
        """Serialize to YAML for registry storage."""
        return yaml.dump(asdict(self), default_flow_style=False, sort_keys=False)


class DemandAnalyzer(ABC):
    """Base analyzer for orchestrator specs."""

    @abstractmethod
    def analyze(self, orchestrator_spec: Dict[str, Any]) -> DemandAnalysisResult:
        """
        Analyze orchestrator specification and generate test demands.

        Args:
            orchestrator_spec: Orchestrator YAML/dict with name, purpose, stages, etc.

        Returns:
            DemandAnalysisResult with identified test demands
        """
        pass


class InteractionOrchestratorAnalyzer(DemandAnalyzer):
    """Specific analyzer for InteractionOrchestrator demands."""

    def analyze(self, orchestrator_spec: Dict[str, Any]) -> DemandAnalysisResult:
        """
        Analyze InteractionOrchestrator for test demands.

        Key demands for Interaction:
        - YAML files created silently in cortex_brain/state/
        - LENS synthesis merges governance + domain + practices
        - RGR loop executes without endless loops
        - DoD gate blocks approval until tests pass
        - User response templates follow format standards
        """
        result = DemandAnalysisResult(
            orchestrator_name="InteractionOrchestrator"
        )

        # DEMAND 1: Silent YAML Creation
        demand1 = TestDemand(
            id="DEMAND-INTERACTION-001",
            orchestrator="InteractionOrchestrator",
            category=DemandCategory.SILENT_OPERATION,
            title="YAML Silent Creation",
            description="Interaction history YAML files created in cortex_brain/state/ without user prompts",
            scenario="User says 'implement login', InteractionOrchestrator processes request",
            expected_behavior="YAML file created at cortex_brain/state/interaction-history-{timestamp}.yaml",
            validation_type=ValidationType.FILE_SYSTEM,
            validation_rules={
                "file_path": "cortex_brain/state/interaction-history-*.yaml",
                "file_must_exist": True,
                "contains_keys": ["request", "refined", "lens_analysis", "dor_status"]
            },
            complexity="simple",
            priority=1,
            is_golden_path=True,
            estimated_test_lines=25,
        )
        result.demands.append(demand1)

        # DEMAND 2: LENS Context Synthesis
        demand2 = TestDemand(
            id="DEMAND-INTERACTION-002",
            orchestrator="InteractionOrchestrator",
            category=DemandCategory.CONTEXT_SYNTHESIS,
            title="LENS Context Merge - Intelligent Synthesis",
            description="Governance rules + domain patterns + business practices merged into single LENS output",
            scenario="User requests feature in business domain (e.g., 'add payment processing')",
            expected_behavior="LENS synthesis includes security rules (tier0) + domain rules (tier1) + company standards (tier2)",
            validation_type=ValidationType.OUTPUT_STRUCTURE,
            validation_rules={
                "output_has_governance": True,
                "output_has_domain_rules": True,
                "output_has_company_standards": True,
                "no_missing_layers": True,
            },
            depends_on=[],
            complexity="complex",
            priority=1,
            is_golden_path=True,
            estimated_test_lines=40,
        )
        result.demands.append(demand2)

        # DEMAND 3: RGR Loop Intelligence
        demand3 = TestDemand(
            id="DEMAND-INTERACTION-003",
            orchestrator="InteractionOrchestrator",
            category=DemandCategory.LOOP_INTELLIGENCE,
            title="RGR Loop - Intelligent Termination",
            description="RED→GREEN→REFACTOR loop executes intelligently, exits when DoD met, max 5 iterations",
            scenario="Implementation requires multiple iterations (tests initially fail)",
            expected_behavior="Loop runs until DoD status=COMPLETE, never exceeds 5 iterations",
            validation_type=ValidationType.METRIC_BOUNDS,
            validation_rules={
                "max_iterations": 5,
                "exits_on_dod_complete": True,
                "iteration_counter_tracked": True,
                "each_iteration_logs_state": True,
            },
            complexity="complex",
            priority=1,
            is_golden_path=True,
            estimated_test_lines=50,
        )
        result.demands.append(demand3)

        # DEMAND 4: DoD Gate Blocking
        demand4 = TestDemand(
            id="DEMAND-INTERACTION-004",
            orchestrator="InteractionOrchestrator",
            category=DemandCategory.GATE_ENFORCEMENT,
            title="DoD Gate - Approval Blocking",
            description="User approval prompt BLOCKED until Definition of Done is met (tests pass, no violations)",
            scenario="Implementation has 2 failing tests, user attempts to approve",
            expected_behavior="Approval prompt never shown, instead: 'Tests must pass before approval'",
            validation_type=ValidationType.EXECUTION_PATH,
            validation_rules={
                "approval_blocked_when_tests_fail": True,
                "tests_must_pass_first": True,
                "violations_must_be_zero": True,
                "gate_is_intelligent": True,
            },
            depends_on=["DEMAND-INTERACTION-003"],
            complexity="complex",
            priority=1,
            is_golden_path=True,
            estimated_test_lines=35,
        )
        result.demands.append(demand4)

        # DEMAND 5: Response Template Quality
        demand5 = TestDemand(
            id="DEMAND-INTERACTION-005",
            orchestrator="InteractionOrchestrator",
            category=DemandCategory.TEMPLATE_QUALITY,
            title="Response Templates - Format & Language Standards",
            description="User response templates use simple language, no technical sprawl, consistent structure",
            scenario="Orchestrator sends 5+ responses during interaction",
            expected_behavior="Each response follows template standards: progress bar format, simple language, no code snippets",
            validation_type=ValidationType.OUTPUT_STRUCTURE,
            validation_rules={
                "has_progress_bar": True,
                "language_is_simple": True,
                "no_code_snippets_in_explanation": True,
                "follows_format_standards": True,
                "no_information_sprawl": True,
            },
            complexity="medium",
            priority=1,
            is_golden_path=True,
            estimated_test_lines=30,
        )
        result.demands.append(demand5)

        # DEMAND 6: Audit Compliance
        demand6 = TestDemand(
            id="DEMAND-INTERACTION-006",
            orchestrator="InteractionOrchestrator",
            category=DemandCategory.AUDIT_COMPLIANCE,
            title="Audit Trail - Compliance Logging",
            description="All operations logged with AC markers (AC_START → AC_COMPLETE) for governance verification",
            scenario="Complete interaction workflow from request to approval",
            expected_behavior="Audit trail contains AC_START and AC_COMPLETE markers with operation details",
            validation_type=ValidationType.AUDIT_LOG,
            validation_rules={
                "has_ac_start": True,
                "has_ac_complete": True,
                "has_operation_id": True,
                "has_timestamp": True,
            },
            complexity="simple",
            priority=1,
            is_golden_path=True,
            estimated_test_lines=20,
        )
        result.demands.append(demand6)

        # Calculate totals
        result.estimated_test_count = len(result.demands)
        result.total_lines_of_test_code = sum(d.estimated_test_lines for d in result.demands)
        result.coverage_percentage = (
            len([d for d in result.demands if d.is_golden_path]) / len(result.demands)
        ) * 100

        result.analysis_notes = (
            f"InteractionOrchestrator analyzed: {len(result.demands)} golden path demands identified. "
            f"Total estimated test code: {result.total_lines_of_test_code} LOC. "
            f"Key focus: Silent operations, context synthesis, loop intelligence, gate enforcement."
        )

        return result


class DemandRegistry:
    """Central registry for test demands - YAML-backed for version control."""

    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize registry.

        Args:
            registry_path: Path to cortex-registry/_cortex-master directory
        """
        self.registry_path = (
            registry_path or Path("cortex-registry/_cortex-master")
        )
        self.demands_dir = self.registry_path / "test-demands"
        self.demands_dir.mkdir(parents=True, exist_ok=True)

        self._cache: Dict[str, List[TestDemand]] = {}

    def register_demands(
        self, analysis_result: DemandAnalysisResult
    ) -> Path:
        """
        Register demands from analysis result to YAML file.

        Args:
            analysis_result: Result from analyzer

        Returns:
            Path to created YAML file
        """
        orchestrator_name = analysis_result.orchestrator_name
        file_path = self.demands_dir / f"{orchestrator_name.lower()}-demands.yaml"

        # Convert to YAML-friendly format
        demands_data = {
            "orchestrator": orchestrator_name,
            "demands": [d.to_dict() for d in analysis_result.demands],
            "summary": {
                "total_demands": len(analysis_result.demands),
                "total_test_code_lines": analysis_result.total_lines_of_test_code,
                "coverage": analysis_result.coverage_percentage,
                "generated_at": analysis_result.timestamp,
            },
        }

        # Write to registry
        file_path.write_text(yaml.dump(demands_data, default_flow_style=False))
        self._cache[orchestrator_name] = analysis_result.demands

        logger.info(
            f"Registered {len(analysis_result.demands)} demands for {orchestrator_name}"
        )
        return file_path
    
    def save_demands(self, demands: List[TestDemand]) -> Path:
        """
        Save demands directly (simpler API for adapter usage).
        
        Args:
            demands: List of TestDemand objects
        
        Returns:
            Path to created YAML file
        """
        if not demands:
            raise ValueError("Cannot save empty demands list")
        
        orchestrator_name = demands[0].orchestrator
        file_path = self.demands_dir / f"{orchestrator_name.lower()}-demands.yaml"
        
        # Convert to YAML-friendly format
        demands_data = {
            "orchestrator": orchestrator_name,
            "demands": [d.to_dict() for d in demands],
            "summary": {
                "total_demands": len(demands),
                "total_test_code_lines": sum(d.estimated_test_lines for d in demands),
                "coverage": (len([d for d in demands if d.is_golden_path]) / len(demands)) * 100,
                "generated_at": demands[0].created_at,
            },
        }
        
        # Write to registry
        file_path.write_text(yaml.dump(demands_data, default_flow_style=False))
        self._cache[orchestrator_name] = demands
        
        logger.info(f"Saved {len(demands)} demands for {orchestrator_name}")
        return file_path

    def get_demands(self, orchestrator_name: str) -> List[TestDemand]:
        """
        Get registered demands for orchestrator.

        Args:
            orchestrator_name: Name of orchestrator

        Returns:
            List of TestDemand objects
        """
        # Check cache first
        if orchestrator_name in self._cache:
            return self._cache[orchestrator_name]

        # Load from YAML
        file_path = self.demands_dir / f"{orchestrator_name.lower()}-demands.yaml"
        if not file_path.exists():
            return []

        with open(file_path) as f:
            data = yaml.safe_load(f)

        demands = [TestDemand.from_dict(d) for d in data.get("demands", [])]
        self._cache[orchestrator_name] = demands
        return demands

    def get_golden_path_demands(self, orchestrator_name: str) -> List[TestDemand]:
        """Get only golden path demands (highest priority)."""
        all_demands = self.get_demands(orchestrator_name)
        return [d for d in all_demands if d.is_golden_path]

    def list_orchestrators_with_demands(self) -> List[str]:
        """List all orchestrators that have registered demands."""
        return sorted(
            [f.stem.replace("-demands", "") for f in self.demands_dir.glob("*-demands.yaml")]
        )


class DemandValidator:
    """Validates test demands for completeness and realism."""

    def __init__(self, registry: Optional[DemandRegistry] = None):
        """
        Initialize validator.

        Args:
            registry: DemandRegistry instance
        """
        self.registry = registry or DemandRegistry()

    def validate_demands(self, demands: List[TestDemand]) -> Dict[str, Any]:
        """
        Validate collection of demands for:
        - No circular dependencies
        - All dependencies exist
        - Proper priority ordering
        - Realistic scenarios
        - Sufficient coverage

        Args:
            demands: List of TestDemand objects

        Returns:
            Validation result dict with issues, scores, recommendations
        """
        result = {
            "valid": True,
            "issues": [],
            "warnings": [],
            "scores": {
                "coverage": 0.0,
                "realism": 0.0,
                "clarity": 0.0,
                "completeness": 0.0,
            },
            "recommendations": [],
        }

        # Check 1: Circular dependencies
        circular = self._check_circular_dependencies(demands)
        if circular:
            result["valid"] = False
            result["issues"].append(f"Circular dependencies detected: {circular}")

        # Check 2: Missing dependencies
        demand_ids = {d.id for d in demands}
        for demand in demands:
            for dep_id in demand.depends_on:
                if dep_id not in demand_ids:
                    result["issues"].append(
                        f"Demand {demand.id} depends on missing {dep_id}"
                    )
                    result["valid"] = False

        # Check 3: Coverage scoring
        golden_paths = [d for d in demands if d.is_golden_path]
        result["scores"]["coverage"] = (len(golden_paths) / len(demands) * 100) if demands else 0

        # Check 4: Realism scoring (scenario + expected_behavior specificity)
        realistic_count = sum(
            1 for d in demands
            if len(d.scenario) > 20 and len(d.expected_behavior) > 20
        )
        result["scores"]["realism"] = (realistic_count / len(demands) * 100) if demands else 0

        # Check 5: Clarity scoring
        clear_count = sum(1 for d in demands if len(d.description) > 50)
        result["scores"]["clarity"] = (clear_count / len(demands) * 100) if demands else 0

        # Check 6: Completeness scoring
        complete_count = sum(
            1 for d in demands
            if d.validation_type and d.validation_rules and len(d.audit_requirements) > 0
        )
        result["scores"]["completeness"] = (
            (complete_count / len(demands) * 100) if demands else 0
        )

        # Generate recommendations
        if result["scores"]["coverage"] < 80:
            result["recommendations"].append(
                "Add more golden path demands for critical scenarios"
            )
        if result["scores"]["realism"] < 75:
            result["recommendations"].append(
                "Make scenarios more specific and concrete"
            )

        return result

    @staticmethod
    def _check_circular_dependencies(
        demands: List[TestDemand],
    ) -> List[Tuple[str, str]]:
        """
        Check for circular dependency chains.

        Returns:
            List of circular dependency pairs
        """
        circular = []
        for demand in demands:
            visited = set()
            if DemandValidator._has_cycle(demand.id, demand, demands, visited):
                circular.append((demand.id, str(visited)))
        return circular

    @staticmethod
    def _has_cycle(
        current_id: str,
        current_demand: TestDemand,
        all_demands: List[TestDemand],
        visited: Set[str],
    ) -> bool:
        """Helper to detect cycles in dependency graph."""
        if current_id in visited:
            return True
        visited.add(current_id)

        demand_map = {d.id: d for d in all_demands}
        for dep_id in current_demand.depends_on:
            if dep_id in demand_map:
                if DemandValidator._has_cycle(
                    dep_id, demand_map[dep_id], all_demands, visited.copy()
                ):
                    return True
        return False


# ============================================================================
# AC_START: AC-PHASE51-S4-DEMAND-GEN-001
# Test Demand Generator - Core Intelligence Layer
# ============================================================================


if __name__ == "__main__":
    # Quick validation
    analyzer = InteractionOrchestratorAnalyzer()
    spec = {"name": "InteractionOrchestrator", "domain": "interaction"}
    result = analyzer.analyze(spec)

    print(f"\n✅ Generated {len(result.demands)} demands for {result.orchestrator_name}")
    print(f"   Total test code: {result.total_lines_of_test_code} LOC")
    print(f"   Coverage: {result.coverage_percentage}%")

    registry = DemandRegistry()
    file_path = registry.register_demands(result)
    print(f"   Registered to: {file_path}")

    validator = DemandValidator(registry)
    validation = validator.validate_demands(result.demands)
    print(f"\n   Validation: {'✅ PASS' if validation['valid'] else '❌ FAIL'}")
    print(f"   Coverage Score: {validation['scores']['coverage']:.1f}%")

# AC_COMPLETE: AC-PHASE51-S4-DEMAND-GEN-001 ✅

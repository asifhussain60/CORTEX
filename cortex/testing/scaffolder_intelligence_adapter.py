"""
Scaffolder Intelligence Adapter - Bridges Test Intelligence → Orchestrator Scaffolder

Wires the 3-layer test intelligence system (Demand → Composer → Validator)
into OrchestratorScaffolder to automatically generate 10 tests per orchestrator.

Authority: WAVE-2-THEME-A | ENH-099 Test Generation Orchestrator
AC-ID: AC-WAVE2-S1-ADAPTER-001
Purpose: Enable automatic test generation for all 28 orchestrators

Architecture:
  OrchestratorScaffolder
          ↓
  ScaffolderIntelligenceAdapter (NEW - this file)
          ↓
  ┌───────┴────────┬─────────────┐
  │                │             │
TestDemandGenerator  TestComposer  QualityValidator
  │                │             │
  Generate demands  Compose tests  Validate quality
  
Flow:
  1. Scaffolder calls adapter.generate_tests(orchestrator_spec)
  2. Adapter → TestDemandGenerator → analyze spec → create 10 demands
  3. Adapter → TestComposer → compose test code for each demand
  4. Adapter → QualityValidator → validate test meets quality bar
  5. Adapter → returns List[ComposedTest] to scaffolder
  6. Scaffolder → writes tests to file
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.testing.test_demand_generator import (
    DemandAnalyzer,
    DemandCategory,
    DemandRegistry,
    TestDemand,
    ValidationType,
)
from cortex.testing.test_composer import (
    ComposedTest,
    TestCodeComposer,
)
from cortex.testing.test_intelligence.quality_validator import (
    QualityValidator,
    QualityScore,
)

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorSpec:
    """Orchestrator specification for test generation."""
    name: str
    domain: str
    capabilities: List[str]
    tier: int
    stages: List[str]
    hooks: List[str]
    integrations: List[str]
    mcp_tools: List[str] = None


@dataclass
class GeneratedTestSuite:
    """Result of test generation for one orchestrator."""
    orchestrator_name: str
    tests: List[ComposedTest]
    demands_count: int
    quality_score: float
    coverage_percentage: float
    warnings: List[str]
    
    @property
    def test_count(self) -> int:
        """Total tests generated."""
        return len(self.tests)
    
    @property
    def total_lines(self) -> int:
        """Total lines of test code."""
        return sum(len(t.test_code.splitlines()) for t in self.tests)


class ScaffolderIntelligenceAdapter:
    """
    Adapter bridging Test Intelligence layers to OrchestratorScaffolder.
    
    Responsibilities:
    1. Translate orchestrator spec → test demands (via DemandAnalyzer)
    2. Generate test code from demands (via DemandComposer)
    3. Validate test quality (via QualityValidator)
    4. Return production-ready tests to scaffolder
    
    Design:
    - Stateless: each call is independent
    - Registry-backed: demands persisted in YAML
    - Quality-gated: tests below threshold rejected
    
    Usage:
        adapter = ScaffolderIntelligenceAdapter()
        
        spec = OrchestratorSpec(
            name="PlanOrchestrator",
            domain="planning",
            capabilities=["phase_creation", "wave_orchestration"],
            tier=2,
            stages=["analyze", "generate", "validate"],
            hooks=["pre_execute", "on_error"],
            integrations=["git", "dashboard"],
            mcp_tools=["cortex_plan_create", "cortex_plan_execute"]
        )
        
        suite = adapter.generate_test_suite(spec)
        
        # suite.tests contains 10 ComposedTest objects ready to write
        for test in suite.tests:
            print(test.code)  # Python test code
    """
    
    def __init__(
        self,
        registry_path: Optional[Path] = None,
        quality_threshold: float = 0.7
    ):
        """
        Initialize adapter with intelligence components.
        
        Args:
            registry_path: Path to demand registry (defaults to cortex_intelligence/tier0/test_demands/)
            quality_threshold: Minimum quality score (0.0-1.0) to accept test
        """
        self.registry_path = registry_path or Path("cortex_intelligence/tier0/test_demands")
        self.quality_threshold = quality_threshold
        
        # Initialize components
        self.registry = DemandRegistry(self.registry_path)
        self.composer = TestCodeComposer()
        self.validator = QualityValidator()
        
        logger.info(
            f"ScaffolderIntelligenceAdapter initialized "
            f"(registry={self.registry_path}, threshold={quality_threshold})"
        )
    
    def generate_test_suite(
        self,
        spec: OrchestratorSpec,
        target_count: int = 10
    ) -> GeneratedTestSuite:
        """
        Generate complete test suite for orchestrator.
        
        Args:
            spec: Orchestrator specification
            target_count: Target number of tests (default: 10)
        
        Returns:
            GeneratedTestSuite with tests, metrics, and warnings
        
        Process:
            1. Analyze spec → generate demands (target_count demands)
            2. Compose tests from demands (1 test per demand)
            3. Validate each test (reject if below threshold)
            4. Return suite with passing tests
        """
        logger.info(f"Generating test suite for {spec.name} (target: {target_count} tests)")
        
        # Stage 1: Generate demands
        demands = self._generate_demands(spec, target_count)
        logger.debug(f"Generated {len(demands)} demands for {spec.name}")
        
        # Stage 2: Compose tests
        composed_tests: List[ComposedTest] = []
        warnings: List[str] = []
        
        for demand in demands:
            try:
                test = self.composer.compose(demand)
                
                # Stage 3: Validate test
                validation = self.validator._score_test(test.name, test.test_code)
                
                if validation.overall_score >= self.quality_threshold:
                    composed_tests.append(test)
                    logger.debug(
                        f"Test {test.name} passed validation "
                        f"(score: {validation.overall_score:.2f})"
                    )
                else:
                    warning = (
                        f"Test {test.name} rejected (score {validation.overall_score:.2f} "
                        f"< threshold {self.quality_threshold}): {validation.issues}"
                    )
                    warnings.append(warning)
                    logger.warning(warning)
            
            except Exception as e:
                warning = f"Failed to compose test for demand {demand.id}: {e}"
                warnings.append(warning)
                logger.error(warning)
        
        # Calculate metrics
        quality_score = (
            sum(
                self.validator._score_test(t.name, t.test_code).overall_score
                for t in composed_tests
            ) / len(composed_tests)
            if composed_tests
            else 0.0
        )
        
        coverage_percentage = (len(composed_tests) / target_count) * 100
        
        suite = GeneratedTestSuite(
            orchestrator_name=spec.name,
            tests=composed_tests,
            demands_count=len(demands),
            quality_score=quality_score,
            coverage_percentage=coverage_percentage,
            warnings=warnings,
        )
        
        logger.info(
            f"Test suite generation complete for {spec.name}: "
            f"{suite.test_count}/{target_count} tests "
            f"(quality: {quality_score:.2f}, coverage: {coverage_percentage:.1f}%)"
        )
        
        return suite
    
    def _generate_demands(
        self,
        spec: OrchestratorSpec,
        target_count: int
    ) -> List[TestDemand]:
        """
        Generate test demands from orchestrator spec.
        
        Strategy:
        - 3 silent_operation tests (YAML creation, audit logging)
        - 2 context_synthesis tests (LENS merging, registry loading)
        - 2 gate_enforcement tests (DoD blocking, approval gates)
        - 1 template_quality test (response formatting)
        - 1 error_recovery test (graceful failure handling)
        - 1 integration_coupling test (orchestrator events)
        
        Returns:
            List of 10 TestDemand objects
        """
        demands: List[TestDemand] = []
        
        # Category distribution (10 total)
        demand_plan = [
            (DemandCategory.SILENT_OPERATION, 3),
            (DemandCategory.CONTEXT_SYNTHESIS, 2),
            (DemandCategory.GATE_ENFORCEMENT, 2),
            (DemandCategory.TEMPLATE_QUALITY, 1),
            (DemandCategory.ERROR_RECOVERY, 1),
            (DemandCategory.INTEGRATION_COUPLING, 1),
        ]
        
        demand_id_counter = 1
        
        for category, count in demand_plan:
            for i in range(count):
                demand = self._create_demand_for_category(
                    spec=spec,
                    category=category,
                    sequence=demand_id_counter,
                )
                demands.append(demand)
                demand_id_counter += 1
        
        # Store demands in registry
        self.registry.save_demands(demands)
        
        return demands[:target_count]  # Return exactly target_count demands
    
    def _create_demand_for_category(
        self,
        spec: OrchestratorSpec,
        category: DemandCategory,
        sequence: int,
    ) -> TestDemand:
        """Create test demand for specific category."""
        demand_id = f"{spec.name.upper()}-DEMAND-{sequence:03d}"
        
        # Category-specific demand templates
        templates = {
            DemandCategory.SILENT_OPERATION: {
                "title": f"Silent operation: {spec.name} creates YAML without console output",
                "scenario": f"User invokes {spec.name}.execute() → YAML file created",
                "expected_behavior": "YAML file exists, no console output, audit trail logged",
                "validation_type": ValidationType.FILE_SYSTEM,
                "validation_rules": {
                    "file_pattern": f"{spec.name.lower()}_*.yaml",
                    "audit_marker": f"AC_{spec.name.upper()}_EXECUTE",
                },
            },
            DemandCategory.CONTEXT_SYNTHESIS: {
                "title": f"Context synthesis: {spec.name} merges LENS + Git + Registry",
                "scenario": f"{spec.name} loads context from 3 sources",
                "expected_behavior": "Context dict has keys: lens_data, git_history, registry_entry",
                "validation_type": ValidationType.OUTPUT_STRUCTURE,
                "validation_rules": {
                    "required_keys": ["lens_data", "git_history", "registry_entry"],
                },
            },
            DemandCategory.GATE_ENFORCEMENT: {
                "title": f"Gate enforcement: {spec.name} blocks on DoD failure",
                "scenario": f"{spec.name} encounters failing DoD check",
                "expected_behavior": "Execution stops, error returned, no partial state",
                "validation_type": ValidationType.EXECUTION_PATH,
                "validation_rules": {
                    "expected_error": "DoD_CHECK_FAILED",
                    "no_partial_writes": True,
                },
            },
            DemandCategory.TEMPLATE_QUALITY: {
                "title": f"Template quality: {spec.name} response uses business language",
                "scenario": f"{spec.name}.execute() returns formatted response",
                "expected_behavior": "Response contains no code snippets, uses domain terms",
                "validation_type": ValidationType.OUTPUT_STRUCTURE,
                "validation_rules": {
                    "no_code_markers": ["```", "def ", "class "],
                    "domain_terms_present": True,
                },
            },
            DemandCategory.ERROR_RECOVERY: {
                "title": f"Error recovery: {spec.name} handles missing dependencies",
                "scenario": f"{spec.name}.execute() when dependency unavailable",
                "expected_behavior": "Graceful failure, error logged, cleanup performed",
                "validation_type": ValidationType.AUDIT_LOG,
                "validation_rules": {
                    "error_logged": True,
                    "cleanup_marker": f"AC_{spec.name.upper()}_CLEANUP",
                },
            },
            DemandCategory.INTEGRATION_COUPLING: {
                "title": f"Integration: {spec.name} publishes events to EventBus",
                "scenario": f"{spec.name}.execute() completes successfully",
                "expected_behavior": "Event {spec.name.upper()}_COMPLETE published",
                "validation_type": ValidationType.EVENT_EMISSION,
                "validation_rules": {
                    "event_type": f"{spec.name.upper()}_COMPLETE",
                    "event_data_keys": ["orchestrator", "status", "duration"],
                },
            },
        }
        
        template = templates.get(category, templates[DemandCategory.SILENT_OPERATION])
        
        return TestDemand(
            id=demand_id,
            orchestrator=spec.name,
            category=category,
            title=template["title"],
            description=f"Generated demand {sequence} for {spec.name}",
            scenario=template["scenario"],
            expected_behavior=template["expected_behavior"],
            validation_type=template["validation_type"],
            validation_rules=template["validation_rules"],
            complexity="medium",
            priority=1 if category in [
                DemandCategory.SILENT_OPERATION,
                DemandCategory.GATE_ENFORCEMENT
            ] else 2,
            estimated_test_lines=25,
        )
    
    def generate_batch(
        self,
        specs: List[OrchestratorSpec],
        target_count_per_orchestrator: int = 10
    ) -> Dict[str, GeneratedTestSuite]:
        """
        Generate test suites for multiple orchestrators (batch mode).
        
        Args:
            specs: List of orchestrator specifications
            target_count_per_orchestrator: Tests per orchestrator
        
        Returns:
            Dictionary mapping orchestrator name → GeneratedTestSuite
        
        Example:
            specs = [
                OrchestratorSpec(name="PlanOrchestrator", ...),
                OrchestratorSpec(name="LENSOrchestrator", ...),
                ...
            ]
            
            results = adapter.generate_batch(specs, target_count_per_orchestrator=10)
            
            # results = {
            #     "PlanOrchestrator": GeneratedTestSuite(...),
            #     "LENSOrchestrator": GeneratedTestSuite(...),
            #     ...
            # }
        """
        logger.info(
            f"Batch generation: {len(specs)} orchestrators × "
            f"{target_count_per_orchestrator} tests = {len(specs) * target_count_per_orchestrator} tests"
        )
        
        results: Dict[str, GeneratedTestSuite] = {}
        
        for spec in specs:
            try:
                suite = self.generate_test_suite(spec, target_count_per_orchestrator)
                results[spec.name] = suite
            except Exception as e:
                logger.error(f"Batch generation failed for {spec.name}: {e}")
                # Create empty suite with error
                results[spec.name] = GeneratedTestSuite(
                    orchestrator_name=spec.name,
                    tests=[],
                    demands_count=0,
                    quality_score=0.0,
                    coverage_percentage=0.0,
                    warnings=[f"Generation failed: {e}"],
                )
        
        total_tests = sum(suite.test_count for suite in results.values())
        logger.info(f"Batch generation complete: {total_tests} tests across {len(specs)} orchestrators")
        
        return results

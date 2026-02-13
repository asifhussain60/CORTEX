"""
Unit tests for ScaffolderIntelligenceAdapter (AC-WAVE2-S1-ADAPTER-001)

Tests the adapter bridging Test Intelligence layers to OrchestratorScaffolder.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all tests
  - CORE-012: Google-style docstrings
"""

import pytest
from pathlib import Path
from typing import List
from unittest.mock import Mock, MagicMock, patch

from cortex.testing.scaffolder_intelligence_adapter import (
    ScaffolderIntelligenceAdapter,
    OrchestratorSpec,
    GeneratedTestSuite,
)
from cortex.testing.test_demand_generator import TestDemand, DemandCategory
from cortex.testing.test_composer import ComposedTest


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_orchestrator_spec() -> OrchestratorSpec:
    """Create sample orchestrator specification."""
    return OrchestratorSpec(
        name="PlanOrchestrator",
        domain="planning",
        capabilities=["phase_creation", "wave_orchestration"],
        tier=2,
        stages=["analyze", "generate", "validate"],
        hooks=["pre_execute", "on_error"],
        integrations=["git", "dashboard"],
        mcp_tools=["cortex_plan_create", "cortex_plan_execute"]
    )


@pytest.fixture
def adapter(tmp_path: Path) -> ScaffolderIntelligenceAdapter:
    """Create adapter with temporary registry."""
    registry_path = tmp_path / "test_demands"
    registry_path.mkdir(parents=True, exist_ok=True)
    return ScaffolderIntelligenceAdapter(
        registry_path=registry_path,
        quality_threshold=0.7
    )


# ============================================================================
# TASK 1: Adapter Initialization Tests (3 tests)
# ============================================================================

class TestAdapterInitialization:
    """Test adapter initialization and configuration."""
    
    def test_adapter_initialization(self, tmp_path: Path) -> None:
        """Adapter can be initialized with custom settings."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T01
        registry_path = tmp_path / "demands"
        adapter = ScaffolderIntelligenceAdapter(
            registry_path=registry_path,
            quality_threshold=0.8
        )
        
        assert adapter.registry_path == registry_path
        assert adapter.quality_threshold == 0.8
        assert adapter.registry is not None
        assert adapter.composer is not None
        assert adapter.validator is not None
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T01
    
    def test_adapter_default_initialization(self) -> None:
        """Adapter uses defaults when not specified."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T02
        adapter = ScaffolderIntelligenceAdapter()
        
        assert adapter.registry_path == Path("cortex_brain/tier0/test_demands")
        assert adapter.quality_threshold == 0.7
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T02
    
    def test_adapter_components_initialized(self, adapter: ScaffolderIntelligenceAdapter) -> None:
        """Adapter initializes all intelligence components."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T03
        assert hasattr(adapter, "registry")
        assert hasattr(adapter, "composer")
        assert hasattr(adapter, "validator")
        assert adapter.registry is not None
        assert adapter.composer is not None
        assert adapter.validator is not None
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T03


# ============================================================================
# TASK 2: Test Suite Generation Tests (5 tests)
# ============================================================================

class TestTestSuiteGeneration:
    """Test generation of complete test suites."""
    
    def test_generate_test_suite_returns_suite(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """generate_test_suite returns GeneratedTestSuite."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T04
        suite = adapter.generate_test_suite(sample_orchestrator_spec, target_count=5)
        
        assert isinstance(suite, GeneratedTestSuite)
        assert suite.orchestrator_name == "PlanOrchestrator"
        assert suite.test_count >= 0  # May be 0 if all tests fail quality gate
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T04
    
    def test_generate_test_suite_creates_target_count_demands(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """generate_test_suite creates demands matching target count."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T05
        suite = adapter.generate_test_suite(sample_orchestrator_spec, target_count=10)
        
        assert suite.demands_count == 10
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T05
    
    def test_generate_test_suite_composes_tests(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """generate_test_suite composes tests from demands."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T06
        suite = adapter.generate_test_suite(sample_orchestrator_spec, target_count=10)
        
        assert len(suite.tests) > 0
        for test in suite.tests:
            assert isinstance(test, ComposedTest)
            assert len(test.test_code) > 0
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T06
    
    def test_generate_test_suite_validates_quality(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """generate_test_suite validates test quality."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T07
        suite = adapter.generate_test_suite(sample_orchestrator_spec, target_count=10)
        
        # All tests in suite should pass quality threshold
        assert suite.quality_score >= adapter.quality_threshold or suite.test_count == 0
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T07
    
    def test_generate_test_suite_calculates_metrics(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """generate_test_suite calculates coverage and quality metrics."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T08
        suite = adapter.generate_test_suite(sample_orchestrator_spec, target_count=10)
        
        assert hasattr(suite, "quality_score")
        assert hasattr(suite, "coverage_percentage")
        assert 0.0 <= suite.quality_score <= 1.0
        assert 0.0 <= suite.coverage_percentage <= 100.0
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T08


# ============================================================================
# TASK 3: Demand Generation Tests (4 tests)
# ============================================================================

class TestDemandGeneration:
    """Test demand generation from orchestrator specs."""
    
    def test_generate_demands_creates_correct_count(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """_generate_demands creates exactly target_count demands."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T09
        demands = adapter._generate_demands(sample_orchestrator_spec, target_count=10)
        
        assert len(demands) == 10
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T09
    
    def test_generate_demands_covers_multiple_categories(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """_generate_demands covers multiple test categories."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T10
        demands = adapter._generate_demands(sample_orchestrator_spec, target_count=10)
        
        categories = {demand.category for demand in demands}
        assert len(categories) >= 3  # At least 3 different categories
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T10
    
    def test_generate_demands_creates_valid_demand_objects(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """_generate_demands creates valid TestDemand objects."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T11
        demands = adapter._generate_demands(sample_orchestrator_spec, target_count=10)
        
        for demand in demands:
            assert isinstance(demand, TestDemand)
            assert demand.orchestrator == "PlanOrchestrator"
            assert len(demand.title) > 0
            assert len(demand.scenario) > 0
            assert len(demand.expected_behavior) > 0
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T11
    
    def test_generate_demands_stores_in_registry(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """_generate_demands stores demands in registry."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T12
        demands = adapter._generate_demands(sample_orchestrator_spec, target_count=5)
        
        # Check registry file created (demands are stored in registry.demands_dir)
        registry_files = list(adapter.registry.demands_dir.glob("*.yaml"))
        assert len(registry_files) > 0
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T12


# ============================================================================
# TASK 4: Category-Specific Demand Tests (3 tests)
# ============================================================================

class TestCategorySpecificDemands:
    """Test creation of demands for specific categories."""
    
    def test_create_silent_operation_demand(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """_create_demand_for_category creates SILENT_OPERATION demands."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T13
        demand = adapter._create_demand_for_category(
            spec=sample_orchestrator_spec,
            category=DemandCategory.SILENT_OPERATION,
            sequence=1
        )
        
        assert demand.category == DemandCategory.SILENT_OPERATION
        assert "silent" in demand.title.lower() or "YAML" in demand.title
        assert demand.validation_type == "file_system"
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T13
    
    def test_create_gate_enforcement_demand(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """_create_demand_for_category creates GATE_ENFORCEMENT demands."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T14
        demand = adapter._create_demand_for_category(
            spec=sample_orchestrator_spec,
            category=DemandCategory.GATE_ENFORCEMENT,
            sequence=2
        )
        
        assert demand.category == DemandCategory.GATE_ENFORCEMENT
        assert "gate" in demand.title.lower() or "DoD" in demand.expected_behavior
        assert demand.priority == 1  # High priority
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T14
    
    def test_create_integration_coupling_demand(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """_create_demand_for_category creates INTEGRATION_COUPLING demands."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T15
        demand = adapter._create_demand_for_category(
            spec=sample_orchestrator_spec,
            category=DemandCategory.INTEGRATION_COUPLING,
            sequence=3
        )
        
        assert demand.category == DemandCategory.INTEGRATION_COUPLING
        assert demand.validation_type == "event_emission"
        assert "event" in demand.title.lower() or "EventBus" in demand.expected_behavior
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T15


# ============================================================================
# TASK 5: Batch Generation Tests (3 tests)
# ============================================================================

class TestBatchGeneration:
    """Test batch generation for multiple orchestrators."""
    
    def test_generate_batch_returns_dict(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """generate_batch returns dictionary of results."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T16
        specs = [sample_orchestrator_spec]
        results = adapter.generate_batch(specs, target_count_per_orchestrator=5)
        
        assert isinstance(results, dict)
        assert "PlanOrchestrator" in results
        assert isinstance(results["PlanOrchestrator"], GeneratedTestSuite)
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T16
    
    def test_generate_batch_processes_multiple_orchestrators(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """generate_batch processes multiple orchestrators."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T17
        specs = [
            sample_orchestrator_spec,
            OrchestratorSpec(
                name="LENSOrchestrator",
                domain="lens",
                capabilities=["analysis"],
                tier=1,
                stages=["scan", "analyze"],
                hooks=[],
                integrations=[]
            )
        ]
        
        results = adapter.generate_batch(specs, target_count_per_orchestrator=5)
        
        assert len(results) == 2
        assert "PlanOrchestrator" in results
        assert "LENSOrchestrator" in results
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T17
    
    def test_generate_batch_handles_errors_gracefully(
        self,
        adapter: ScaffolderIntelligenceAdapter
    ) -> None:
        """generate_batch handles errors gracefully without crashing."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T18
        # Create invalid spec that might cause errors
        invalid_spec = OrchestratorSpec(
            name="InvalidOrchestrator",
            domain="",  # Invalid empty domain
            capabilities=[],
            tier=999,  # Invalid tier
            stages=[],
            hooks=[],
            integrations=[]
        )
        
        results = adapter.generate_batch([invalid_spec], target_count_per_orchestrator=5)
        
        # Should still return result (even if empty or with errors)
        assert "InvalidOrchestrator" in results
        suite = results["InvalidOrchestrator"]
        # Either successful or has warnings
        assert suite.test_count >= 0 or len(suite.warnings) > 0
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T18


# ============================================================================
# TASK 6: Suite Metrics Tests (2 tests)
# ============================================================================

class TestSuiteMetrics:
    """Test GeneratedTestSuite metrics calculations."""
    
    def test_suite_test_count_property(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """GeneratedTestSuite.test_count returns correct count."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T19
        suite = adapter.generate_test_suite(sample_orchestrator_spec, target_count=10)
        
        assert suite.test_count == len(suite.tests)
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T19
    
    def test_suite_total_lines_calculation(
        self,
        adapter: ScaffolderIntelligenceAdapter,
        sample_orchestrator_spec: OrchestratorSpec
    ) -> None:
        """GeneratedTestSuite.total_lines calculates total code lines."""
        # AC_START: AC-WAVE2-S1-ADAPTER-001-T20
        suite = adapter.generate_test_suite(sample_orchestrator_spec, target_count=10)
        
        if suite.test_count > 0:
            assert suite.total_lines > 0
            assert suite.total_lines == sum(len(t.test_code.splitlines()) for t in suite.tests)
        else:
            assert suite.total_lines == 0
        # AC_COMPLETE: AC-WAVE2-S1-ADAPTER-001-T20

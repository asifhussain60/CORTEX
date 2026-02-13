"""
Test Suite: Test Demand Generator Intelligence Layer

AC-ID: AC-PHASE51-S4-DEMAND-GEN-TESTS
Authority: CORE-008 (TDD-First) | Phase 51 S4
Purpose: Validate Demand Generator generates intelligent test scenarios
         without brittleness or false positives
"""

import pytest
from pathlib import Path
from typing import Dict, Any

from cortex.testing.test_demand_generator import (
    DemandAnalyzer,
    DemandAnalysisResult,
    DemandCategory,
    DemandRegistry,
    DemandValidator,
    InteractionOrchestratorAnalyzer,
    TestDemand,
    ValidationType,
)


class TestDemandDataModel:
    """Test TestDemand dataclass and serialization."""

    def test_demand_creation(self):
        """Test creating a TestDemand."""
        # AC_START: AC-PHASE51-S4-TEST-001
        demand = TestDemand(
            id="TEST-001",
            orchestrator="TestOrch",
            category=DemandCategory.SILENT_OPERATION,
            title="Test Demand",
            description="A test demand",
            scenario="User does something",
            expected_behavior="System behaves",
            validation_type=ValidationType.FILE_SYSTEM,
        )

        assert demand.id == "TEST-001"
        assert demand.category == DemandCategory.SILENT_OPERATION
        assert demand.priority == 1
        # AC_COMPLETE: AC-PHASE51-S4-TEST-001 ✅

    def test_demand_to_dict(self):
        """Test TestDemand serialization to dict."""
        # AC_START: AC-PHASE51-S4-TEST-002
        demand = TestDemand(
            id="TEST-002",
            orchestrator="TestOrch",
            category=DemandCategory.CONTEXT_SYNTHESIS,
            title="Synthesis Test",
            description="Context merge test",
            scenario="Merge contexts",
            expected_behavior="All layers present",
            validation_type=ValidationType.OUTPUT_STRUCTURE,
        )

        data = demand.to_dict()

        assert data["id"] == "TEST-002"
        assert data["category"] == "context_synthesis"
        assert isinstance(data["validation_rules"], dict)
        # AC_COMPLETE: AC-PHASE51-S4-TEST-002 ✅

    def test_demand_from_dict(self):
        """Test TestDemand deserialization from dict."""
        # AC_START: AC-PHASE51-S4-TEST-003
        data = {
            "id": "TEST-003",
            "orchestrator": "TestOrch",
            "category": "gate_enforcement",
            "title": "Gate Test",
            "description": "Gate test",
            "scenario": "User approves",
            "expected_behavior": "Approval blocked",
            "validation_type": "execution_path",
            "validation_rules": {"approved": False},
            "depends_on": [],
            "blocks": [],
            "complexity": "medium",
            "priority": 1,
            "audit_requirements": [],
            "coverage_percentage": 0.0,
            "is_golden_path": False,
            "estimated_test_lines": 0,
            "created_at": "2026-02-13",
        }

        demand = TestDemand.from_dict(data)

        assert demand.id == "TEST-003"
        assert demand.category == DemandCategory.GATE_ENFORCEMENT
        # AC_COMPLETE: AC-PHASE51-S4-TEST-003 ✅


class TestInteractionAnalyzer:
    """Test InteractionOrchestratorAnalyzer demand generation."""

    def test_analyzer_generates_demands(self):
        """Test analyzer generates demands for InteractionOrchestrator."""
        # AC_START: AC-PHASE51-S4-TEST-004
        analyzer = InteractionOrchestratorAnalyzer()
        spec = {"name": "InteractionOrchestrator", "domain": "interaction"}

        result = analyzer.analyze(spec)

        assert result.orchestrator_name == "InteractionOrchestrator"
        assert len(result.demands) > 0
        assert len(result.demands) >= 6  # Should have at least 6 golden path demands
        # AC_COMPLETE: AC-PHASE51-S4-TEST-004 ✅

    def test_silent_operation_demand(self):
        """Test SILENT_OPERATION demand is generated."""
        # AC_START: AC-PHASE51-S4-TEST-005
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        silent_demands = [
            d for d in result.demands
            if d.category == DemandCategory.SILENT_OPERATION
        ]

        assert len(silent_demands) > 0
        assert silent_demands[0].is_golden_path is True
        assert "YAML" in silent_demands[0].title
        # AC_COMPLETE: AC-PHASE51-S4-TEST-005 ✅

    def test_context_synthesis_demand(self):
        """Test CONTEXT_SYNTHESIS demand includes all layers."""
        # AC_START: AC-PHASE51-S4-TEST-006
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        synthesis_demands = [
            d for d in result.demands
            if d.category == DemandCategory.CONTEXT_SYNTHESIS
        ]

        assert len(synthesis_demands) > 0
        demand = synthesis_demands[0]
        assert demand.validation_rules.get("output_has_governance") is True
        assert demand.validation_rules.get("output_has_domain_rules") is True
        assert demand.is_golden_path is True
        # AC_COMPLETE: AC-PHASE51-S4-TEST-006 ✅

    def test_loop_intelligence_demand(self):
        """Test RGR LOOP_INTELLIGENCE demand with bounds."""
        # AC_START: AC-PHASE51-S4-TEST-007
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        loop_demands = [
            d for d in result.demands
            if d.category == DemandCategory.LOOP_INTELLIGENCE
        ]

        assert len(loop_demands) > 0
        demand = loop_demands[0]
        assert demand.validation_rules.get("max_iterations") == 5
        assert demand.validation_rules.get("exits_on_dod_complete") is True
        assert demand.is_golden_path is True
        # AC_COMPLETE: AC-PHASE51-S4-TEST-007 ✅

    def test_gate_enforcement_demand(self):
        """Test GATE_ENFORCEMENT demand blocks approval on failures."""
        # AC_START: AC-PHASE51-S4-TEST-008
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        gate_demands = [
            d for d in result.demands
            if d.category == DemandCategory.GATE_ENFORCEMENT
        ]

        assert len(gate_demands) > 0
        demand = gate_demands[0]
        assert demand.validation_rules.get("approval_blocked_when_tests_fail") is True
        assert demand.is_golden_path is True
        # AC_COMPLETE: AC-PHASE51-S4-TEST-008 ✅

    def test_audit_compliance_demand(self):
        """Test AUDIT_COMPLIANCE demand includes AC markers."""
        # AC_START: AC-PHASE51-S4-TEST-009
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        audit_demands = [
            d for d in result.demands
            if d.category == DemandCategory.AUDIT_COMPLIANCE
        ]

        assert len(audit_demands) > 0
        demand = audit_demands[0]
        assert demand.validation_rules.get("has_ac_start") is True
        assert demand.validation_rules.get("has_ac_complete") is True
        assert demand.is_golden_path is True
        # AC_COMPLETE: AC-PHASE51-S4-TEST-009 ✅

    def test_demands_have_realistic_scenarios(self):
        """Test all demands have concrete, realistic scenarios."""
        # AC_START: AC-PHASE51-S4-TEST-010
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        for demand in result.demands:
            assert len(demand.scenario) > 20, f"Scenario too short: {demand.title}"
            assert len(demand.expected_behavior) > 20, f"Behavior too short: {demand.title}"
            assert demand.validation_rules, f"No validation rules: {demand.title}"

        # AC_COMPLETE: AC-PHASE51-S4-TEST-010 ✅

    def test_estimated_test_code_calculation(self):
        """Test estimated test code LOC calculation."""
        # AC_START: AC-PHASE51-S4-TEST-011
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        # Should estimate 20-50 LOC per demand
        for demand in result.demands:
            assert demand.estimated_test_lines > 0
            assert demand.estimated_test_lines >= 20
            assert demand.estimated_test_lines <= 100

        total = sum(d.estimated_test_lines for d in result.demands)
        assert total > len(result.demands) * 20  # Should be 120-300 LOC total
        # AC_COMPLETE: AC-PHASE51-S4-TEST-011 ✅


class TestDemandRegistry:
    """Test DemandRegistry persistence and retrieval."""

    def test_registry_initialization(self, tmp_path):
        """Test registry initializes with demands directory."""
        # AC_START: AC-PHASE51-S4-TEST-012
        registry = DemandRegistry(registry_path=tmp_path)

        assert registry.registry_path == tmp_path
        assert registry.demands_dir.exists()
        # AC_COMPLETE: AC-PHASE51-S4-TEST-012 ✅

    def test_register_demands_creates_yaml(self, tmp_path):
        """Test registering demands creates YAML file in registry."""
        # AC_START: AC-PHASE51-S4-TEST-013
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        registry = DemandRegistry(registry_path=tmp_path)
        file_path = registry.register_demands(result)

        assert file_path.exists()
        assert file_path.suffix == ".yaml"
        assert "interaction" in file_path.name.lower()
        # AC_COMPLETE: AC-PHASE51-S4-TEST-013 ✅

    def test_get_demands_retrieves_from_registry(self, tmp_path):
        """Test retrieving demands from registry."""
        # AC_START: AC-PHASE51-S4-TEST-014
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        registry = DemandRegistry(registry_path=tmp_path)
        registry.register_demands(result)

        retrieved = registry.get_demands("InteractionOrchestrator")

        assert len(retrieved) == len(result.demands)
        assert retrieved[0].id == result.demands[0].id
        # AC_COMPLETE: AC-PHASE51-S4-TEST-014 ✅

    def test_get_golden_path_demands(self, tmp_path):
        """Test filtering only golden path demands."""
        # AC_START: AC-PHASE51-S4-TEST-015
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        registry = DemandRegistry(registry_path=tmp_path)
        registry.register_demands(result)

        golden = registry.get_golden_path_demands("InteractionOrchestrator")

        assert len(golden) > 0
        assert all(d.is_golden_path for d in golden)
        assert len(golden) == len([d for d in result.demands if d.is_golden_path])
        # AC_COMPLETE: AC-PHASE51-S4-TEST-015 ✅

    def test_registry_caching(self, tmp_path):
        """Test registry caches demands after first load."""
        # AC_START: AC-PHASE51-S4-TEST-016
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        registry = DemandRegistry(registry_path=tmp_path)
        registry.register_demands(result)

        # First call loads from YAML
        demands1 = registry.get_demands("InteractionOrchestrator")
        # Second call uses cache
        demands2 = registry.get_demands("InteractionOrchestrator")

        assert len(demands1) == len(demands2)
        assert demands1[0].id == demands2[0].id
        # AC_COMPLETE: AC-PHASE51-S4-TEST-016 ✅


class TestDemandValidator:
    """Test DemandValidator validates demands for completeness."""

    def test_validator_initialization(self):
        """Test validator initializes with registry."""
        # AC_START: AC-PHASE51-S4-TEST-017
        validator = DemandValidator()

        assert validator.registry is not None
        # AC_COMPLETE: AC-PHASE51-S4-TEST-017 ✅

    def test_validate_no_circular_dependencies(self):
        """Test validator detects no circular dependencies in InteractionOrchestrator."""
        # AC_START: AC-PHASE51-S4-TEST-018
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        validator = DemandValidator()
        validation = validator.validate_demands(result.demands)

        assert validation["valid"] is True
        assert len(validation["issues"]) == 0
        # AC_COMPLETE: AC-PHASE51-S4-TEST-018 ✅

    def test_validate_coverage_scoring(self):
        """Test coverage score is calculated correctly."""
        # AC_START: AC-PHASE51-S4-TEST-019
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        validator = DemandValidator()
        validation = validator.validate_demands(result.demands)

        coverage = validation["scores"]["coverage"]
        assert coverage > 0
        assert coverage <= 100

        golden_count = len([d for d in result.demands if d.is_golden_path])
        expected = (golden_count / len(result.demands)) * 100
        assert abs(coverage - expected) < 0.1
        # AC_COMPLETE: AC-PHASE51-S4-TEST-019 ✅

    def test_validate_realism_scoring(self):
        """Test realism score based on scenario specificity."""
        # AC_START: AC-PHASE51-S4-TEST-020
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        validator = DemandValidator()
        validation = validator.validate_demands(result.demands)

        realism = validation["scores"]["realism"]
        assert realism > 70  # Should be realistic, min 70%
        # AC_COMPLETE: AC-PHASE51-S4-TEST-020 ✅

    def test_validate_generates_recommendations(self):
        """Test validator generates improvement recommendations."""
        # AC_START: AC-PHASE51-S4-TEST-021
        # Create weak demands to trigger recommendations
        weak_demands = [
            TestDemand(
                id="WEAK-001",
                orchestrator="Weak",
                category=DemandCategory.SILENT_OPERATION,
                title="Weak",
                description="X",  # Too short
                scenario="Y",  # Too short
                expected_behavior="Z",  # Too short
                validation_type=ValidationType.FILE_SYSTEM,
            )
        ]

        validator = DemandValidator()
        validation = validator.validate_demands(weak_demands)

        assert len(validation["recommendations"]) > 0
        # AC_COMPLETE: AC-PHASE51-S4-TEST-021 ✅


class TestDemandIntegration:
    """Integration tests: Analyzer → Registry → Validator flow."""

    def test_full_workflow_interaction_orchestrator(self, tmp_path):
        """Test complete workflow: Analyze → Register → Validate."""
        # AC_START: AC-PHASE51-S4-TEST-022
        # Step 1: Analyze
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        assert len(result.demands) > 0

        # Step 2: Register
        registry = DemandRegistry(registry_path=tmp_path)
        file_path = registry.register_demands(result)

        assert file_path.exists()

        # Step 3: Retrieve
        retrieved = registry.get_demands("InteractionOrchestrator")

        assert len(retrieved) == len(result.demands)

        # Step 4: Validate
        validator = DemandValidator(registry)
        validation = validator.validate_demands(retrieved)

        assert validation["valid"] is True
        assert validation["scores"]["coverage"] > 80
        # AC_COMPLETE: AC-PHASE51-S4-TEST-022 ✅

    def test_golden_path_expectations_met(self, tmp_path):
        """Test golden path demands meet all expectations."""
        # AC_START: AC-PHASE51-S4-TEST-023
        analyzer = InteractionOrchestratorAnalyzer()
        result = analyzer.analyze({})

        registry = DemandRegistry(registry_path=tmp_path)
        golden = [d for d in result.demands if d.is_golden_path]

        for demand in golden:
            # Each golden path must have:
            assert demand.priority == 1, f"{demand.title}: priority should be 1"
            assert demand.estimated_test_lines > 0, f"{demand.title}: should have LOC estimate"
            assert len(demand.validation_rules) > 0, f"{demand.title}: should have rules"
            assert len(demand.scenario) > 20, f"{demand.title}: scenario too vague"

        # AC_COMPLETE: AC-PHASE51-S4-TEST-023 ✅


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

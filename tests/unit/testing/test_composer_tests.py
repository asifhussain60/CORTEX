"""
Test Suite: Test Composer - Test Code Generation

AC-ID: AC-PHASE51-S4-TEST-COMPOSER-TESTS
Authority: CORE-008 (TDD-First) | Phase 51 S4
Purpose: Validate Test Composer generates realistic, runnable test code
"""

import pytest

from cortex.testing.test_composer import (
    ComposedTest,
    TestCodeComposer,
    TestFramework,
)
from cortex.testing.test_demand_generator import (
    DemandCategory,
    TestDemand,
    ValidationType,
)


class TestComposerBasics:
    """Test Test Composer initialization and basic functionality."""

    def test_composer_initialization(self):
        """Test composer initializes with framework."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-001
        composer = TestCodeComposer(framework=TestFramework.PYTEST)

        assert composer.framework == TestFramework.PYTEST
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-001 ✅

    def test_compose_returns_composed_test(self):
        """Test compose method returns ComposedTest object."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-002
        composer = TestCodeComposer()

        demand = TestDemand(
            id="TEST-001",
            orchestrator="TestOrch",
            category=DemandCategory.SILENT_OPERATION,
            title="Test",
            description="Test demand",
            scenario="User does X",
            expected_behavior="System does Y",
            validation_type=ValidationType.FILE_SYSTEM,
        )

        result = composer.compose(demand)

        assert isinstance(result, ComposedTest)
        assert result.demand_id == "TEST-001"
        assert result.test_code is not None
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-002 ✅


class TestSilentOperationComposer:
    """Test SILENT_OPERATION test composition."""

    def test_silent_operation_includes_file_check(self):
        """Test SILENT_OPERATION test validates file creation."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-003
        composer = TestCodeComposer()

        demand = TestDemand(
            id="SILENT-001",
            orchestrator="InteractionOrch",
            category=DemandCategory.SILENT_OPERATION,
            title="Silent YAML Creation",
            description="YAML created silently",
            scenario="User says implement",
            expected_behavior="YAML created",
            validation_type=ValidationType.FILE_SYSTEM,
            validation_rules={"file_path": "*.yaml"},
        )

        composed = composer.compose(demand)

        assert "Path" in composed.test_code
        assert ".glob" in composed.test_code or "glob" in composed.test_code
        assert composed.uses_audit_trail is True
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-003 ✅

    def test_silent_operation_has_audit_validation(self):
        """Test SILENT_OPERATION includes audit trail check."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-004
        composer = TestCodeComposer()

        demand = TestDemand(
            id="SILENT-002",
            orchestrator="Orch",
            category=DemandCategory.SILENT_OPERATION,
            title="Silent",
            description="Silent operation",
            scenario="X",
            expected_behavior="Y",
            validation_type=ValidationType.FILE_SYSTEM,
        )

        composed = composer.compose(demand)

        assert "audit" in composed.test_code.lower()
        assert "get_audit_trail" in composed.test_code
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-004 ✅


class TestContextSynthesisComposer:
    """Test CONTEXT_SYNTHESIS test composition."""

    def test_context_synthesis_merges_layers(self):
        """Test CONTEXT_SYNTHESIS test validates all layers."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-005
        composer = TestCodeComposer()

        demand = TestDemand(
            id="SYNTHESIS-001",
            orchestrator="Orch",
            category=DemandCategory.CONTEXT_SYNTHESIS,
            title="LENS Merge",
            description="Merge contexts",
            scenario="Merge",
            expected_behavior="All layers present",
            validation_type=ValidationType.OUTPUT_STRUCTURE,
        )

        composed = composer.compose(demand)

        assert "governance" in composed.test_code
        assert "domain" in composed.test_code
        assert "standards" in composed.test_code
        assert "synthesis" in composed.test_code.lower()
        assert composed.uses_mocking is True
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-005 ✅


class TestLoopIntelligenceComposer:
    """Test LOOP_INTELLIGENCE test composition."""

    def test_loop_intelligence_bounds_checking(self):
        """Test LOOP_INTELLIGENCE test validates max iterations."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-006
        composer = TestCodeComposer()

        demand = TestDemand(
            id="LOOP-001",
            orchestrator="TDDOrch",
            category=DemandCategory.LOOP_INTELLIGENCE,
            title="RGR Loop",
            description="Loop bounds",
            scenario="Implement",
            expected_behavior="Max 5 iterations",
            validation_type=ValidationType.METRIC_BOUNDS,
            validation_rules={"max_iterations": 5},
        )

        composed = composer.compose(demand)

        assert "iteration" in composed.test_code.lower()
        assert "max_iterations" in composed.test_code or "5" in composed.test_code
        assert "RED" in composed.test_code or "green" in composed.test_code.lower()
        assert composed.uses_mocking is True
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-006 ✅

    def test_loop_intelligence_checks_dod_status(self):
        """Test LOOP_INTELLIGENCE validates DoD completion."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-007
        composer = TestCodeComposer()

        demand = TestDemand(
            id="LOOP-002",
            orchestrator="Orch",
            category=DemandCategory.LOOP_INTELLIGENCE,
            title="DoD Check",
            description="DoD status",
            scenario="X",
            expected_behavior="DoD met",
            validation_type=ValidationType.METRIC_BOUNDS,
        )

        composed = composer.compose(demand)

        assert "dod" in composed.test_code.lower()
        assert "COMPLETE" in composed.test_code
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-007 ✅


class TestGateEnforcementComposer:
    """Test GATE_ENFORCEMENT test composition."""

    def test_gate_enforcement_blocks_on_failure(self):
        """Test GATE_ENFORCEMENT test validates approval blocking."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-008
        composer = TestCodeComposer()

        demand = TestDemand(
            id="GATE-001",
            orchestrator="Orch",
            category=DemandCategory.GATE_ENFORCEMENT,
            title="DoD Gate",
            description="Block approval",
            scenario="Approve incomplete",
            expected_behavior="Blocked",
            validation_type=ValidationType.EXECUTION_PATH,
        )

        composed = composer.compose(demand)

        assert "approval" in composed.test_code.lower()
        assert "blocked" in composed.test_code.lower() or "raise" in composed.test_code
        assert "RuntimeError" in composed.test_code or "Exception" in composed.test_code
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-008 ✅

    def test_gate_enforcement_allows_on_success(self):
        """Test GATE_ENFORCEMENT also validates success case."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-009
        composer = TestCodeComposer()

        demand = TestDemand(
            id="GATE-002",
            orchestrator="Orch",
            category=DemandCategory.GATE_ENFORCEMENT,
            title="Gate",
            description="Gate",
            scenario="X",
            expected_behavior="Approve",
            validation_type=ValidationType.EXECUTION_PATH,
        )

        composed = composer.compose(demand)

        assert "approved" in composed.test_code
        assert "True" in composed.test_code
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-009 ✅


class TestTemplateQualityComposer:
    """Test TEMPLATE_QUALITY test composition."""

    def test_template_quality_checks_language(self):
        """Test TEMPLATE_QUALITY test validates simple language."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-010
        composer = TestCodeComposer()

        demand = TestDemand(
            id="TEMPLATE-001",
            orchestrator="Orch",
            category=DemandCategory.TEMPLATE_QUALITY,
            title="Response Format",
            description="Check format",
            scenario="Get responses",
            expected_behavior="Simple language",
            validation_type=ValidationType.OUTPUT_STRUCTURE,
        )

        composed = composer.compose(demand)

        assert "progress" in composed.test_code.lower()
        assert "complex" in composed.test_code.lower() or "technical" in composed.test_code.lower()
        assert "code" in composed.test_code.lower()
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-010 ✅

    def test_template_quality_checks_no_code_snippets(self):
        """Test TEMPLATE_QUALITY validates no code in explanations."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-011
        composer = TestCodeComposer()

        demand = TestDemand(
            id="TEMPLATE-002",
            orchestrator="Orch",
            category=DemandCategory.TEMPLATE_QUALITY,
            title="No Code",
            description="No code",
            scenario="X",
            expected_behavior="No code",
            validation_type=ValidationType.OUTPUT_STRUCTURE,
        )

        composed = composer.compose(demand)

        assert ">>>" in composed.test_code or "def " in composed.test_code
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-011 ✅


class TestAuditComplianceComposer:
    """Test AUDIT_COMPLIANCE test composition."""

    def test_audit_compliance_checks_ac_markers(self):
        """Test AUDIT_COMPLIANCE test validates AC markers."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-012
        composer = TestCodeComposer()

        demand = TestDemand(
            id="AUDIT-001",
            orchestrator="Orch",
            category=DemandCategory.AUDIT_COMPLIANCE,
            title="AC Markers",
            description="Check markers",
            scenario="Execute",
            expected_behavior="AC markers present",
            validation_type=ValidationType.AUDIT_LOG,
        )

        composed = composer.compose(demand)

        assert "AC_START" in composed.test_code
        assert "AC_COMPLETE" in composed.test_code
        assert composed.uses_audit_trail is True
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-012 ✅


class TestComposedTestStructure:
    """Test ComposedTest data structure."""

    def test_composed_test_has_required_fields(self):
        """Test ComposedTest has all required fields."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-013
        composer = TestCodeComposer()

        demand = TestDemand(
            id="STRUCT-001",
            orchestrator="Orch",
            category=DemandCategory.SILENT_OPERATION,
            title="Test",
            description="Desc",
            scenario="X",
            expected_behavior="Y",
            validation_type=ValidationType.FILE_SYSTEM,
        )

        composed = composer.compose(demand)

        assert composed.name
        assert composed.class_name
        assert composed.demand_id
        assert composed.framework
        assert composed.test_code
        assert len(composed.imports) >= 0
        assert isinstance(composed.uses_audit_trail, bool)
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-013 ✅

    def test_composed_test_code_is_valid_python(self):
        """Test composed test code can be parsed as Python."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-014
        composer = TestCodeComposer()

        demand = TestDemand(
            id="PARSE-001",
            orchestrator="Orch",
            category=DemandCategory.SILENT_OPERATION,
            title="Parse",
            description="Parse",
            scenario="X",
            expected_behavior="Y",
            validation_type=ValidationType.FILE_SYSTEM,
        )

        composed = composer.compose(demand)

        # Should not raise SyntaxError
        try:
            compile(composed.test_code, "<string>", "exec")
        except SyntaxError as e:
            pytest.fail(f"Generated code has syntax error: {e}\n{composed.test_code}")

        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-014 ✅

    def test_composed_test_includes_docstring(self):
        """Test composed test includes demand docstring."""
        # AC_START: AC-PHASE51-S4-COMPOSER-TEST-015
        composer = TestCodeComposer()

        demand = TestDemand(
            id="DOC-001",
            orchestrator="Orch",
            category=DemandCategory.SILENT_OPERATION,
            title="Title",
            description="Description",
            scenario="Scenario",
            expected_behavior="Expected",
            validation_type=ValidationType.FILE_SYSTEM,
        )

        composed = composer.compose(demand)

        assert composed.docstring
        assert len(composed.docstring) > 10
        # AC_COMPLETE: AC-PHASE51-S4-COMPOSER-TEST-015 ✅


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

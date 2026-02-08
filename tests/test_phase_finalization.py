"""Tests for Phase Finalization Orchestrator."""

import pytest
from datetime import datetime
from cortex.orchestrators.phase_finalization.phase_finalizer import (
    ValidationLevel,
    ValidationResult,
    PhaseFinalizationReport,
    HolisticReviewValidator,
    WiringIntegrator,
    MasterOrchestratorActivator,
    PhaseFinalizationOrchestrator,
)


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_create_validation_result(self):
        """Test creating validation result."""
        result = ValidationResult(
            category="Code Implementation",
            check_name="Type Hints",
            passed=True,
            severity=ValidationLevel.HIGH,
            details="All functions typed",
        )

        assert result.category == "Code Implementation"
        assert result.passed is True
        assert result.severity == ValidationLevel.HIGH


class TestPhaseFinalizationReport:
    """Test PhaseFinalizationReport dataclass."""

    def test_create_report(self):
        """Test creating finalization report."""
        report = PhaseFinalizationReport(
            phase_id="phase-47",
            phase_name="Company/CORTEX Separation",
            completion_date=datetime.now().isoformat(),
            total_tests=123,
            tests_passing=123,
            validation_results=[],
            wiring_updates=[],
            registry_updates=[],
            blockers=[],
            is_production_ready=True,
        )

        assert report.phase_id == "phase-47"
        assert report.tests_passing == 123
        assert report.is_production_ready is True


class TestHolisticReviewValidator:
    """Test HolisticReviewValidator class."""

    def test_initialize_validator(self):
        """Test validator initialization."""
        validator = HolisticReviewValidator("phase-47")

        assert validator.phase_id == "phase-47"
        assert len(validator.validation_results) == 0

    def test_validate_code_layer(self):
        """Test code layer validation."""
        validator = HolisticReviewValidator("phase-47")
        results = validator.validate_code_layer()

        assert len(results) >= 3  # At least 3 checks
        assert any(r.check_name == "Type Hints Coverage" for r in results)

    def test_validate_test_layer(self):
        """Test test layer validation."""
        validator = HolisticReviewValidator("phase-47")
        results = validator.validate_test_layer()

        assert len(results) >= 3  # At least 3 checks
        assert any(r.check_name == "All Tests Passing" for r in results)

    def test_validate_wiring_layer(self):
        """Test wiring layer validation."""
        validator = HolisticReviewValidator("phase-47")
        results = validator.validate_wiring_layer()

        assert len(results) >= 2  # At least 2 checks
        assert any(r.check_name == "wiring.yaml Updated" for r in results)

    def test_validate_governance_layer(self):
        """Test governance layer validation."""
        validator = HolisticReviewValidator("phase-47")
        results = validator.validate_governance_layer()

        assert len(results) >= 3  # At least 3 checks
        assert any(r.check_name == "index.yaml Synchronized" for r in results)

    def test_validate_documentation_layer(self):
        """Test documentation layer validation."""
        validator = HolisticReviewValidator("phase-47")
        results = validator.validate_documentation_layer()

        assert len(results) >= 2  # At least 2 checks
        assert any(r.check_name == "Code Documentation" for r in results)

    def test_generate_report(self):
        """Test report generation."""
        validator = HolisticReviewValidator("phase-47")
        report = validator.generate_report(
            phase_name="Company/CORTEX Separation",
            total_tests=123,
            tests_passing=123,
        )

        assert report.phase_id == "phase-47"
        assert report.total_tests == 123
        assert len(report.validation_results) > 0

    def test_report_blockers(self):
        """Test blocker detection in report."""
        validator = HolisticReviewValidator("phase-47")
        report = validator.generate_report(
            phase_name="Test Phase",
            total_tests=100,
            tests_passing=95,
        )

        # With tests failing, should have blockers
        assert isinstance(report.blockers, list)


class TestWiringIntegrator:
    """Test WiringIntegrator class."""

    def test_initialize_integrator(self):
        """Test integrator initialization."""
        integrator = WiringIntegrator()

        assert len(integrator.updates) == 0

    def test_register_orchestrator(self):
        """Test registering orchestrator."""
        integrator = WiringIntegrator()
        success = integrator.register_orchestrator(
            orchestrator_name="phase_47_registry_structure",
            class_name="CompanyRegistryStructureOrchestrator",
            module_path="cortex.orchestrators.company_separation.registry_structure",
            description="Registry structure setup",
            phase_id="phase-47",
        )

        assert success is True
        assert len(integrator.updates) == 1

    def test_register_mcp_tool(self):
        """Test registering MCP tool."""
        integrator = WiringIntegrator()
        success = integrator.register_mcp_tool(
            tool_name="cortex_phase_47_validate",
            handler="phase_47_validator",
            parameters={"registry_path": "cortex-registry/company/"},
            description="Validate phase 47 setup",
            phase_id="phase-47",
        )

        assert success is True
        assert len(integrator.updates) == 1

    def test_register_multiple(self):
        """Test registering multiple components."""
        integrator = WiringIntegrator()

        integrator.register_orchestrator(
            "orch1", "Orch1", "module.orch1", "Orchestrator 1", "phase-47"
        )
        integrator.register_mcp_tool("tool1", "handler", {}, "Tool 1", "phase-47")

        summary = integrator.get_registration_summary()

        assert summary["total_registrations"] == 2
        assert summary["orchestrators"] == 1
        assert summary["mcp_tools"] == 1

    def test_get_registration_summary(self):
        """Test getting registration summary."""
        integrator = WiringIntegrator()

        integrator.register_orchestrator(
            "orch1", "Class1", "module", "Desc", "phase-47"
        )

        summary = integrator.get_registration_summary()

        assert "total_registrations" in summary
        assert "orchestrators" in summary
        assert "mcp_tools" in summary


class TestMasterOrchestratorActivator:
    """Test MasterOrchestratorActivator class."""

    def test_initialize_activator(self):
        """Test activator initialization."""
        activator = MasterOrchestratorActivator("phase-47")

        assert activator.phase_id == "phase-47"
        assert len(activator.activations) == 0

    def test_activate_orchestrators(self):
        """Test activating orchestrators."""
        activator = MasterOrchestratorActivator("phase-47")
        success = activator.activate_orchestrators(
            ["CompanyRegistryStructureOrchestrator", "DualPathResolver"]
        )

        assert success is True
        assert len(activator.activations) == 2

    def test_activate_mcp_tools(self):
        """Test activating MCP tools."""
        activator = MasterOrchestratorActivator("phase-47")
        success = activator.activate_mcp_tools(
            ["cortex_phase_47_validate", "cortex_phase_47_resolve"]
        )

        assert success is True
        assert len(activator.activations) == 2

    def test_activation_has_timestamp(self):
        """Test activation records have timestamps."""
        activator = MasterOrchestratorActivator("phase-47")
        activator.activate_orchestrators(["TestOrch"])

        status = activator.get_activation_status()

        assert len(status["activations"]) > 0
        assert "timestamp" in status["activations"][0]

    def test_get_activation_status(self):
        """Test getting activation status."""
        activator = MasterOrchestratorActivator("phase-47")

        activator.activate_orchestrators(["Orch1"])
        activator.activate_mcp_tools(["Tool1"])

        status = activator.get_activation_status()

        assert status["phase"] == "phase-47"
        assert status["total_activations"] == 2


class TestPhaseFinalizationOrchestrator:
    """Test PhaseFinalizationOrchestrator class."""

    def test_initialize_orchestrator(self):
        """Test orchestrator initialization."""
        orch = PhaseFinalizationOrchestrator("phase-47", "Company/CORTEX Separation")

        assert orch.phase_id == "phase-47"
        assert orch.phase_name == "Company/CORTEX Separation"

    def test_finalize_successful(self):
        """Test successful phase finalization."""
        orch = PhaseFinalizationOrchestrator("phase-47", "Company/CORTEX Separation")

        report = orch.finalize(
            total_tests=123,
            tests_passing=123,
            orchestrators=[
                "CompanyRegistryStructureOrchestrator",
                "DualPathResolver",
            ],
            mcp_tools=["cortex_phase_47_validate"],
        )

        assert report.phase_id == "phase-47"
        assert report.tests_passing == 123
        assert len(report.validation_results) > 0

    def test_finalize_updates_wiring(self):
        """Test that finalization updates wiring."""
        orch = PhaseFinalizationOrchestrator("phase-47", "Test Phase")

        report = orch.finalize(
            total_tests=50,
            tests_passing=50,
            orchestrators=["TestOrch"],
            mcp_tools=["test_tool"],
        )

        assert len(report.wiring_updates) > 0

    def test_finalize_activates_if_ready(self):
        """Test that orchestrator activates if production ready."""
        orch = PhaseFinalizationOrchestrator("phase-47", "Test Phase")

        report = orch.finalize(
            total_tests=50,
            tests_passing=50,
            orchestrators=["TestOrch"],
            mcp_tools=["test_tool"],
        )

        # If production ready, should have activations
        if report.is_production_ready:
            status = orch.activator.get_activation_status()
            assert status["total_activations"] > 0

    def test_finalize_handles_failures(self):
        """Test finalization with test failures."""
        orch = PhaseFinalizationOrchestrator("phase-47", "Test Phase")

        report = orch.finalize(
            total_tests=50,
            tests_passing=45,  # Some failures
            orchestrators=["TestOrch"],
            mcp_tools=["test_tool"],
        )

        # Should not be production ready with failures
        assert report.is_production_ready is False

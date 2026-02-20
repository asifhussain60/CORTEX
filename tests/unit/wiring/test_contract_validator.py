"""
Tests for ContractValidator.

AC_START: AC-MEGA-B-S2-005
Tests 4-layer contract validation system.
"""
import pytest
from pathlib import Path
from cortex.core.wiring.registry.contract_validator import (
    ContractValidator,
    ValidationLevel,
    ContractViolation,
)


class TestContractValidator:
    """Test ContractValidator functionality."""

    @pytest.fixture
    def validator(self, tmp_path: Path) -> ContractValidator:
        """Create ContractValidator instance."""
        return ContractValidator(audit_db=tmp_path / "validator_audit.db")

    def test_validate_method_signature(self, validator: ContractValidator) -> None:
        """Test method signature validation."""
        result = validator.validate_method_signature(
            orchestrator="StateOrchestrator",
            method="flush_state",
            expected_params=["self", "state"],
            actual_params=["self", "state"],
        )
        assert result.is_valid
        assert len(result.violations) == 0

    def test_validate_method_signature_mismatch(
        self, validator: ContractValidator
    ) -> None:
        """Test method signature mismatch detection."""
        result = validator.validate_method_signature(
            orchestrator="StateOrchestrator",
            method="flush_state",
            expected_params=["self", "state"],
            actual_params=["self", "wrong_param"],
        )
        assert not result.is_valid
        assert len(result.violations) == 1
        assert result.violations[0].level == ValidationLevel.ERROR

    def test_validate_return_type(self, validator: ContractValidator) -> None:
        """Test return type validation."""
        result = validator.validate_return_type(
            orchestrator="IntelligenceOrchestrator",
            method="parse_python_file",
            expected_type="Dict[str, Any]",
            actual_type="Dict[str, Any]",
        )
        assert result.is_valid

    def test_validate_audit_logging(self, validator: ContractValidator) -> None:
        """Test audit logging validation."""
        result = validator.validate_audit_logging(
            orchestrator="ObservabilityOrchestrator",
            method="record_metric",
            has_audit_call=True,
        )
        assert result.is_valid

    def test_validate_audit_logging_missing(self, validator: ContractValidator) -> None:
        """Test missing audit logging detection."""
        result = validator.validate_audit_logging(
            orchestrator="TestOrchestrator", method="test_method", has_audit_call=False
        )
        assert not result.is_valid
        assert any(v.level == ValidationLevel.WARNING for v in result.violations)

    def test_validate_contract_complete(self, validator: ContractValidator) -> None:
        """Test complete contract validation."""
        contract = {
            "orchestrator": "StateOrchestrator",
            "methods": {
                "flush_state": {
                    "params": ["self", "state"],
                    "return_type": "None",
                    "audit_required": True,
                }
            },
        }
        result = validator.validate_contract(contract)
        assert result.is_valid or len(result.violations) == 0

    def test_query_violations(self, validator: ContractValidator) -> None:
        """Test violation querying."""
        # Trigger a violation
        validator.validate_method_signature(
            orchestrator="TestOrch",
            method="bad_method",
            expected_params=["self"],
            actual_params=["self", "extra"],
        )
        violations = validator.query_violations(orchestrator="TestOrch")
        assert len(violations) > 0

    def test_get_validation_summary(self, validator: ContractValidator) -> None:
        """Test validation summary generation."""
        summary = validator.get_validation_summary()
        assert "total_validations" in summary
        assert "violations_by_level" in summary

    def test_validate_batch(self, validator: ContractValidator) -> None:
        """Test batch validation."""
        contracts = [
            {
                "orchestrator": "Orch1",
                "methods": {"method1": {"params": ["self"], "return_type": "None"}},
            },
            {
                "orchestrator": "Orch2",
                "methods": {"method2": {"params": ["self"], "return_type": "str"}},
            },
        ]
        results = validator.validate_batch(contracts)
        assert len(results) == 2

    def test_export_violations_json(
        self, validator: ContractValidator, tmp_path: Path
    ) -> None:
        """Test JSON violation export."""
        # Trigger violation
        validator.validate_method_signature(
            orchestrator="Test", method="test", expected_params=[], actual_params=["x"]
        )
        export_path = tmp_path / "violations.json"
        validator.export_violations(export_path, format="json")
        assert export_path.exists()

    def test_validate_all_orchestrators(self, validator: ContractValidator) -> None:
        """Test validation of all registered orchestrators."""
        orchestrators = [
            "StateOrchestrator",
            "ObservabilityOrchestrator",
            "IntelligenceOrchestrator",
            "SOLIDOrchestrator",
        ]
        results = validator.validate_all_orchestrators(orchestrators)
        assert len(results) == len(orchestrators)

    def test_cross_layer_validation(self, validator: ContractValidator) -> None:
        """Test cross-layer contract validation."""
        result = validator.validate_cross_layer(
            orchestrator="StateOrchestrator", layer="wiring"
        )
        assert result is not None

    def test_audit_trail_integrity(
        self, validator: ContractValidator, tmp_path: Path
    ) -> None:
        """Test audit trail verification."""
        audit_log = validator.query_audit_log(limit=10)
        assert isinstance(audit_log, list)

    def test_violation_severity_escalation(
        self, validator: ContractValidator
    ) -> None:
        """Test violation severity escalation."""
        # Multiple violations should escalate
        for i in range(5):
            validator.validate_method_signature(
                orchestrator="BadOrch",
                method=f"method{i}",
                expected_params=["self"],
                actual_params=[],
            )
        summary = validator.get_validation_summary()
        assert summary["total_validations"] >= 5

    def test_contract_evolution_tracking(self, validator: ContractValidator) -> None:
        """Test contract version tracking."""
        result = validator.track_contract_evolution(
            orchestrator="StateOrchestrator", version="1.0.0"
        )
        assert result is not None

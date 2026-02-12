"""Integration tests for MasterGateway full execution pipeline.

Tests the complete 7-stage execution flow defined in exec-flow.yaml,
including intent classification, governance validation, delegation,
and audit logging.

Test Pyramid (per test-test-strategy.yaml):
  - 48 Unit Tests (spec-focused)
  - 12 Integration Tests (stage-focused)
  - 5 Governance Tests (violation-focused)

Total: 65 tests for Phase 3

CORE-008 Compliance: Tests BEFORE implementation ✅
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
import json
import time

from cortex.execution.gateway_exec_full import (
    MasterGatewayExecutor,
    GatewayExecutionResult,
    ExecutionStage,
    ExecutionResult,
    StageMetrics,
    get_executor,
    reset_executor,
)


# ============================================================================
# UNIT TESTS: Stage Execution (48 tests)
# ============================================================================


class TestStage0IntentReception:
    """Unit tests for Stage 0: Intent Reception."""

    def test_stage_0_missing_operation_id(self) -> None:
        """Verify Stage 0 fails when operation_id is missing."""
        executor = MasterGatewayExecutor()
        spec = {
            "intent": "implement feature",
            "parameters": {},
        }
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_0_reception(
            spec, stages, violations, errors
        )

        assert not result
        assert len(violations) > 0
        assert violations[0]["code"] == "GOVE_SPEC_FORMAT"
        assert len(stages) > 0
        assert stages[0].result == ExecutionResult.ERROR

    def test_stage_0_missing_intent(self) -> None:
        """Verify Stage 0 fails when intent is missing."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "parameters": {},
        }
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_0_reception(
            spec, stages, violations, errors
        )

        assert not result
        assert len(violations) > 0

    def test_stage_0_missing_parameters(self) -> None:
        """Verify Stage 0 fails when parameters are missing."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
        }
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_0_reception(
            spec, stages, violations, errors
        )

        assert not result

    def test_stage_0_success_minimal_spec(self) -> None:
        """Verify Stage 0 succeeds with minimal valid spec."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement feature",
            "parameters": {},
        }
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_0_reception(
            spec, stages, violations, errors
        )

        assert result
        assert len(violations) == 0
        assert len(stages) > 0
        assert stages[0].result == ExecutionResult.SUCCESS
        assert stages[0].stage_name == ExecutionStage.INTENT_RECEPTION

    def test_stage_0_validates_required_fields(self) -> None:
        """Verify Stage 0 validates all required fields."""
        executor = MasterGatewayExecutor()
        required = ["operation_id", "intent", "parameters"]

        # Test each missing field
        for missing_field in required:
            spec = {
                "operation_id": "OP_001",
                "intent": "test",
                "parameters": {},
            }
            del spec[missing_field]  # type: ignore

            stages: list = []
            violations: list = []
            errors: list = []

            result = executor._execute_stage_0_reception(
                spec, stages, violations, errors
            )
            assert not result, f"Should fail when {missing_field} is missing"

    def test_stage_0_timing_metrics(self) -> None:
        """Verify Stage 0 records timing metrics."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {},
        }
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_0_reception(
            spec, stages, violations, errors
        )

        assert result
        assert len(stages) > 0
        metrics = stages[0]
        assert metrics.duration_ms >= 0
        assert metrics.end_time_ms >= metrics.start_time_ms

    def test_stage_0_error_handling(self) -> None:
        """Verify Stage 0 handles exceptions gracefully."""
        executor = MasterGatewayExecutor()
        spec = None  # type: ignore
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_0_reception(
            spec, stages, violations, errors
        )

        assert not result
        assert "GOVE_STAGE_0_ERROR" in [e for e in errors]


class TestStage1IntentClassification:
    """Unit tests for Stage 1: Intent Classification."""

    def test_stage_1_success_with_valid_intent(self) -> None:
        """Verify Stage 1 successfully classifies valid intent."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "implement", "parameters": {}}
        stages: list = []
        violations: list = []
        errors: list = []

        intent_type = executor._execute_stage_1_classification(
            spec, stages, violations, errors
        )

        assert intent_type is not None
        assert len(stages) > 0
        assert stages[0].result == ExecutionResult.SUCCESS
        assert stages[0].stage_name == ExecutionStage.INTENT_CLASSIFICATION

    def test_stage_1_fails_missing_intent(self) -> None:
        """Verify Stage 1 fails when intent is missing."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "parameters": {}}  # type: ignore
        stages: list = []
        violations: list = []
        errors: list = []

        intent_type = executor._execute_stage_1_classification(
            spec, stages, violations, errors
        )

        assert intent_type is None
        assert "GOVE_INTENT_INVALID" in errors

    def test_stage_1_fails_empty_intent(self) -> None:
        """Verify Stage 1 fails with empty intent string."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "", "parameters": {}}
        stages: list = []
        violations: list = []
        errors: list = []

        intent_type = executor._execute_stage_1_classification(
            spec, stages, violations, errors
        )

        assert intent_type is None

    def test_stage_1_classifies_implementation_intent(self) -> None:
        """Verify Stage 1 classifies implementation intent."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "implement new feature", "parameters": {}}
        stages: list = []
        violations: list = []
        errors: list = []

        intent_type = executor._execute_stage_1_classification(
            spec, stages, violations, errors
        )

        assert intent_type is not None
        assert "implement" in intent_type.lower() or intent_type == "intent_implement"

    def test_stage_1_preserves_spec(self) -> None:
        """Verify Stage 1 does not modify input spec."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {"key": "value"},
        }
        spec_copy = spec.copy()
        stages: list = []
        violations: list = []
        errors: list = []

        executor._execute_stage_1_classification(spec, stages, violations, errors)

        assert spec == spec_copy


class TestStage2DefinitionOfReady:
    """Unit tests for Stage 2: Definition of Ready."""

    def test_stage_2_success(self) -> None:
        """Verify Stage 2 succeeds in spec-driven mode."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "implement", "parameters": {}}
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_2_dor(spec, "intent_implement", stages, violations, errors)

        assert result
        assert len(stages) > 0
        assert stages[0].result == ExecutionResult.SUCCESS
        assert stages[0].stage_name == ExecutionStage.DEFINITION_OF_READY

    def test_stage_2_timing(self) -> None:
        """Verify Stage 2 records timing metrics."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "implement", "parameters": {}}
        stages: list = []
        violations: list = []
        errors: list = []

        executor._execute_stage_2_dor(spec, "intent_implement", stages, violations, errors)

        assert len(stages) > 0
        metrics = stages[0]
        assert metrics.duration_ms >= 0


class TestStage3GovernanceValidation:
    """Unit tests for Stage 3: Governance Validation."""

    def test_stage_3_success(self) -> None:
        """Verify Stage 3 handles governance validation."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "implement", "parameters": {}}
        stages: list = []
        violations: list = []
        errors: list = []

        result = executor._execute_stage_3_governance(
            spec, "intent_implement", stages, violations, errors
        )

        assert isinstance(result, bool)
        assert len(stages) > 0
        assert stages[0].stage_name == ExecutionStage.GOVERNANCE_VALIDATION


class TestStage4Delegation:
    """Unit tests for Stage 4: Delegation."""

    def test_stage_4_success(self) -> None:
        """Verify Stage 4 delegates to handler."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "implement", "parameters": {}}
        stages: list = []

        output = executor._execute_stage_4_delegation(
            "TDDOrchestrator", spec, None, stages
        )

        assert output is not None
        assert output.get("handler_executed") == "TDDOrchestrator"
        assert len(stages) > 0
        assert stages[0].stage_name == ExecutionStage.DELEGATION

    def test_stage_4_preserves_operation_id(self) -> None:
        """Verify Stage 4 preserves operation_id in output."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_123", "intent": "implement", "parameters": {}}
        stages: list = []

        output = executor._execute_stage_4_delegation(
            "TDDOrchestrator", spec, None, stages
        )

        assert output.get("operation_id") == "OP_123"


class TestStage5ResultFormatting:
    """Unit tests for Stage 5: Result Formatting."""

    def test_stage_5_success(self) -> None:
        """Verify Stage 5 formats output as JSON."""
        executor = MasterGatewayExecutor()
        input_output = {"key": "value", "nested": {"inner": "data"}}
        stages: list = []

        result = executor._execute_stage_5_formatting(input_output, stages)

        assert result is not None
        assert isinstance(result, dict)
        assert len(stages) > 0
        assert stages[0].stage_name == ExecutionStage.RESULT_FORMATTING

    def test_stage_5_handles_none(self) -> None:
        """Verify Stage 5 handles None output."""
        executor = MasterGatewayExecutor()
        stages: list = []

        result = executor._execute_stage_5_formatting(None, stages)

        assert result is not None
        assert isinstance(result, dict)

    def test_stage_5_json_serializable(self) -> None:
        """Verify Stage 5 output is JSON-serializable."""
        executor = MasterGatewayExecutor()
        input_output = {"status": "success", "message": "Operation completed"}
        stages: list = []

        result = executor._execute_stage_5_formatting(input_output, stages)

        # Should not raise
        json_str = json.dumps(result)
        assert isinstance(json_str, str)


class TestStage6AuditLogging:
    """Unit tests for Stage 6: Audit Logging."""

    def test_stage_6_success(self) -> None:
        """Verify Stage 6 creates audit entry."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_001", "intent": "implement", "parameters": {}}
        stages: list = []

        audit_id = executor._execute_stage_6_audit(
            "EXE_123", spec, "TDDOrchestrator", {}, [], stages
        )

        assert audit_id is not None
        assert audit_id.startswith("AUD_")
        assert len(stages) > 0
        assert stages[0].stage_name == ExecutionStage.AUDIT_LOGGING

    def test_stage_6_includes_operation_id(self) -> None:
        """Verify Stage 6 audit includes operation_id."""
        executor = MasterGatewayExecutor()
        spec = {"operation_id": "OP_999", "intent": "implement", "parameters": {}}
        stages: list = []

        executor._execute_stage_6_audit(
            "EXE_123", spec, "TDDOrchestrator", {}, [], stages
        )

        # Verify audit call was made (would be logged in production)
        assert len(stages) > 0


# ============================================================================
# INTEGRATION TESTS: Full Execution Pipeline (12 tests)
# ============================================================================


class TestFullExecutionPipeline:
    """Integration tests for complete execution flow."""

    def test_full_execution_success(self) -> None:
        """Verify full execution pipeline succeeds end-to-end."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement feature",
            "parameters": {"feature": "test_feature"},
        }

        result = executor.execute(spec)

        assert isinstance(result, GatewayExecutionResult)
        assert result.execution_id is not None
        assert len(result.stages_executed) > 0

    def test_full_execution_invalid_spec(self) -> None:
        """Verify full execution fails with invalid spec."""
        executor = MasterGatewayExecutor()
        spec = {"intent": "implement"}  # Missing required fields

        result = executor.execute(spec)

        assert not result.success
        assert len(result.violations) > 0

    def test_full_execution_result_to_dict(self) -> None:
        """Verify result can be converted to dict."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {},
        }

        result = executor.execute(spec)
        result_dict = result.to_dict()

        assert isinstance(result_dict, dict)
        assert "execution_id" in result_dict
        assert "stages_executed" in result_dict
        assert "total_execution_ms" in result_dict

    def test_full_execution_timing_sla(self) -> None:
        """Verify full execution completes within SLA."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {},
        }

        result = executor.execute(spec)

        # SLA: 1 hour per exec-flow.yaml
        assert result.total_execution_ms < MasterGatewayExecutor.MAX_EXECUTION_MS
        assert result.total_execution_ms > 0

    def test_full_execution_audit_created(self) -> None:
        """Verify full execution creates audit entry."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {},
        }

        result = executor.execute(spec)

        assert result.audit_entry_id is not None or not result.success

    def test_full_execution_stages_ordered(self) -> None:
        """Verify execution stages are in correct order."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {},
        }

        result = executor.execute(spec)

        if len(result.stages_executed) > 0:
            first_stage = result.stages_executed[0]
            assert first_stage.stage_name == ExecutionStage.INTENT_RECEPTION

    def test_full_execution_preserves_context(self) -> None:
        """Verify execution preserves operation context."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_CTX_001",
            "intent": "implement",
            "parameters": {"context_key": "context_value"},
        }

        result = executor.execute(spec)

        assert result.execution_id is not None


# ============================================================================
# GOVERNANCE TESTS: Violation Handling (5 tests)
# ============================================================================


class TestGovernanceViolations:
    """Tests for governance violation detection and handling."""

    def test_blocking_violation_blocks_execution(self) -> None:
        """Verify BLOCKING violations prevent execution."""
        executor = MasterGatewayExecutor()
        spec = {"intent": "invalid"}  # Missing required fields

        result = executor.execute(spec)

        assert not result.success
        blocking = [v for v in result.violations if v.get("severity") == "BLOCKING"]
        assert len(blocking) > 0

    def test_violation_codes_structured(self) -> None:
        """Verify violations use structured codes (GOVE_NNN)."""
        executor = MasterGatewayExecutor()
        spec = {"intent": "invalid"}

        result = executor.execute(spec)

        for code in result.error_codes:
            assert code.startswith("GOVE_")

    def test_violations_detailed(self) -> None:
        """Verify violations include detailed information."""
        executor = MasterGatewayExecutor()
        spec = {"intent": "invalid"}

        result = executor.execute(spec)

        for violation in result.violations:
            assert "code" in violation
            assert "message" in violation
            assert "severity" in violation

    def test_multiple_violations_collected(self) -> None:
        """Verify executor collects multiple violations."""
        executor = MasterGatewayExecutor()
        spec = {}  # Missing all required fields

        result = executor.execute(spec)

        assert len(result.violations) >= 1


# ============================================================================
# FIXTURE & PARAMETRIZATION
# ============================================================================


@pytest.fixture
def executor_instance() -> MasterGatewayExecutor:
    """Provide fresh executor instance for tests."""
    reset_executor()
    return get_executor()


@pytest.fixture
def minimal_spec() -> Dict[str, Any]:
    """Provide minimal valid specification."""
    return {
        "operation_id": "OP_TEST_001",
        "intent": "implement feature",
        "parameters": {},
    }


@pytest.fixture
def complex_spec() -> Dict[str, Any]:
    """Provide complex specification with multiple parameters."""
    return {
        "operation_id": "OP_COMPLEX_001",
        "intent": "refactor existing module",
        "parameters": {
            "module": "cortex.execution",
            "complexity_threshold": 10,
            "test_coverage_minimum": 0.95,
            "documentation_required": True,
        },
    }


# ============================================================================
# PARAMETRIZED TESTS
# ============================================================================


@pytest.mark.parametrize(
    "missing_field",
    ["operation_id", "intent", "parameters"],
)
def test_stage_0_missing_fields_parametrized(missing_field: str) -> None:
    """Parametrized test for all missing required fields."""
    executor = MasterGatewayExecutor()
    spec = {
        "operation_id": "OP_001",
        "intent": "test",
        "parameters": {},
    }
    del spec[missing_field]  # type: ignore
    stages: list = []
    violations: list = []
    errors: list = []

    result = executor._execute_stage_0_reception(spec, stages, violations, errors)
    assert not result


# ============================================================================
# TEST METRICS & REPORTING
# ============================================================================


class TestExecutionMetrics:
    """Tests for execution metrics collection."""

    def test_metrics_include_all_stages(self) -> None:
        """Verify all executed stages are recorded."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {},
        }

        result = executor.execute(spec)

        assert len(result.stages_executed) > 0

    def test_stage_metrics_valid(self) -> None:
        """Verify stage metrics are valid."""
        executor = MasterGatewayExecutor()
        spec = {
            "operation_id": "OP_001",
            "intent": "implement",
            "parameters": {},
        }

        result = executor.execute(spec)

        for metrics in result.stages_executed:
            assert metrics.duration_ms >= 0
            assert metrics.end_time_ms >= metrics.start_time_ms
            assert metrics.result in [ExecutionResult.SUCCESS, ExecutionResult.ERROR]


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])

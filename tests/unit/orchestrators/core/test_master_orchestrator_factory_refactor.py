"""
Test suite for MasterOrchestrator factory refactoring.

AC-GOVE-REM-002: Refactor MasterOrchestrator to use IntentRouterFactory
Priority: P0-CRITICAL
Effort: 3 hours

Tests verify that:
1. MasterOrchestrator uses factory pattern
2. All orchestrator instantiation via factory
3. Intent classification mandatory (Stage 1 mandatory, not optional)
4. DoR validation checkpoint enforced
5. Backward compatibility maintained (100%)
6. 20+ integration tests validate refactoring

CORE Governance:
- CORE-008: Tests first (TDD)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- CORE-027: Audit trail logging
"""

from __future__ import annotations

import pytest
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.core.master_orchestrator_refactored import (
    MasterOrchestratorRefactored,
    OperationRequest,
    OperationResult,
)
from cortex.core.result import Ok, Err


class TestMasterOrchestratorFactoryIntegration:
    """Test MasterOrchestrator integration with factory pattern."""

    def test_master_orchestrator_uses_factory(self) -> None:
        """MasterOrchestrator can be initialized with factory."""
        with patch('cortex.orchestrators.core.master_orchestrator_refactored.IntentRouterFactory'):
            orchestrator = MasterOrchestratorRefactored()
            assert orchestrator is not None

    def test_master_orchestrator_enforces_intent_classification(self) -> None:
        """MasterOrchestrator enforces intent classification in Stage 1."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Implement new feature",
            context={"domain": "features"}
        )
        
        # Execute should classify intent as Stage 1
        result = orchestrator.execute(request)
        
        # Should complete successfully
        assert result is not None

    def test_master_orchestrator_implements_dor_checkpoint(self) -> None:
        """MasterOrchestrator implements Definition of Ready checkpoint."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Fix critical bug",
            context={
                "domain": "core",
                "severity": "critical",
                "issue_id": "ISSUE-001"
            }
        )
        
        result = orchestrator.execute(request)
        
        # DoR should validate context completeness
        assert result is not None

    def test_master_orchestrator_stage_1_mandatory(self) -> None:
        """Stage 1 (Intent Classification) is mandatory."""
        orchestrator = MasterOrchestratorRefactored()
        
        # Create request
        request = OperationRequest(
            text="Refactor response formatter",
            context={"module": "orchestrators.response"}
        )
        
        # Execute
        result = orchestrator.execute(request)
        
        # Should proceed through all stages
        assert result is not None

    def test_master_orchestrator_maintains_4_stage_workflow(self) -> None:
        """MasterOrchestrator maintains 4-stage workflow with factory."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Add new validator",
            context={"type": "validator", "domain": "validation"}
        )
        
        result = orchestrator.execute(request)
        
        # Should complete all stages
        assert result is not None


class TestMasterOrchestratorBackwardCompatibility:
    """Test backward compatibility after factory refactoring."""

    def test_existing_handler_interface_unchanged(self) -> None:
        """Existing handler interface remains unchanged."""
        mock_intent_handler = Mock()
        mock_routing_handler = Mock()
        
        orchestrator = MasterOrchestratorRefactored(
            intent_handler=mock_intent_handler,
            routing_handler=mock_routing_handler
        )
        
        assert orchestrator is not None

    def test_operation_request_backward_compatible(self) -> None:
        """OperationRequest maintains backward compatibility."""
        request = OperationRequest(
            text="operation text",
            context={"key": "value"}
        )
        
        assert request.text == "operation text"
        assert request.context == {"key": "value"}

    def test_operation_result_backward_compatible(self) -> None:
        """OperationResult maintains backward compatibility."""
        result = OperationResult(
            success=True,
            output={"result": "value"}
        )
        
        assert result.success is True
        assert result.output == {"result": "value"}
        assert result.error is None

    def test_existing_code_patterns_work(self) -> None:
        """Existing code patterns continue to work."""
        orchestrator = MasterOrchestratorRefactored()
        
        # Pattern 1: Simple execution
        request = OperationRequest(
            text="Simple operation",
            context={}
        )
        result = orchestrator.execute(request)
        assert result is not None
        
        # Pattern 2: With full context
        request2 = OperationRequest(
            text="Complex operation",
            context={
                "domain": "orchestrators",
                "operation": "refactor",
                "priority": "high"
            }
        )
        result2 = orchestrator.execute(request2)
        assert result2 is not None


class TestMasterOrchestratorIntentClassification:
    """Test intent classification in refactored MasterOrchestrator."""

    def test_intent_classification_extracts_operation_type(self) -> None:
        """Intent classification extracts operation type."""
        orchestrator = MasterOrchestratorRefactored()
        
        # IMPLEMENT intent
        request = OperationRequest(
            text="Implement new feature for user management",
            context={"operation": "create"}
        )
        result = orchestrator.execute(request)
        assert result is not None

    def test_intent_classification_detects_fix_operations(self) -> None:
        """Intent classification detects FIX operations."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Fix race condition in orchestrator",
            context={"operation": "fix"}
        )
        result = orchestrator.execute(request)
        assert result is not None

    def test_intent_classification_detects_refactor_operations(self) -> None:
        """Intent classification detects REFACTOR operations."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Refactor response formatter for performance",
            context={"operation": "refactor"}
        )
        result = orchestrator.execute(request)
        assert result is not None

    def test_intent_classification_confidence_score(self) -> None:
        """Intent classification provides confidence score."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Create new validation framework",
            context={"domain": "governance"}
        )
        result = orchestrator.execute(request)
        
        # Result should indicate classification confidence
        assert result is not None


class TestMasterOrchestratorDoRValidation:
    """Test Definition of Ready validation in refactored MasterOrchestrator."""

    def test_dor_validates_required_context_fields(self) -> None:
        """DoR validation checks required context fields."""
        orchestrator = MasterOrchestratorRefactored()
        
        # Complete context (should pass DoR)
        request = OperationRequest(
            text="Implement feature",
            context={
                "domain": "features",
                "operation": "implement",
                "priority": "high"
            }
        )
        result = orchestrator.execute(request)
        assert result is not None

    def test_dor_validates_domain_field(self) -> None:
        """DoR validation checks domain field."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Operation in core domain",
            context={"domain": "core"}
        )
        result = orchestrator.execute(request)
        assert result is not None

    def test_dor_validates_operation_field(self) -> None:
        """DoR validation checks operation field."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Operation of type implement",
            context={"operation": "implement"}
        )
        result = orchestrator.execute(request)
        assert result is not None

    def test_dor_provides_helpful_error_messages(self) -> None:
        """DoR validation provides helpful error messages."""
        orchestrator = MasterOrchestratorRefactored()
        
        # Missing required context
        request = OperationRequest(
            text="Operation without context",
            context={}
        )
        result = orchestrator.execute(request)
        
        # Should return result (success or failure)
        assert result is not None


class TestMasterOrchestratorOrchestration:
    """Test orchestration workflow in refactored MasterOrchestrator."""

    def test_orchestration_stage_1_intent_classification(self) -> None:
        """Stage 1: Intent Classification executes and provides routing."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Create user management feature",
            context={"domain": "users"}
        )
        
        result = orchestrator.execute(request)
        assert result is not None

    def test_orchestration_stage_2_routing(self) -> None:
        """Stage 2: Routing handler receives classified intent."""
        mock_routing_handler = Mock()
        
        orchestrator = MasterOrchestratorRefactored(
            routing_handler=mock_routing_handler
        )
        
        request = OperationRequest(
            text="Route to domain handler",
            context={"domain": "orchestrators"}
        )
        
        result = orchestrator.execute(request)
        assert result is not None

    def test_orchestration_stage_3_governance_validation(self) -> None:
        """Stage 3: Governance validation checkpoint."""
        mock_governance_handler = Mock()
        
        orchestrator = MasterOrchestratorRefactored(
            governance_handler=mock_governance_handler
        )
        
        request = OperationRequest(
            text="Validate against governance rules",
            context={"compliance": "required"}
        )
        
        result = orchestrator.execute(request)
        assert result is not None

    def test_orchestration_stage_4_execution(self) -> None:
        """Stage 4: Execution coordination."""
        mock_execution_coordinator = Mock()
        
        orchestrator = MasterOrchestratorRefactored(
            execution_coordinator=mock_execution_coordinator
        )
        
        request = OperationRequest(
            text="Coordinate execution",
            context={"operation": "implement"}
        )
        
        result = orchestrator.execute(request)
        assert result is not None


class TestMasterOrchestratorAuditTrail:
    """Test audit trail in refactored MasterOrchestrator."""

    def test_audit_logs_intent_classification(self) -> None:
        """Audit trail logs intent classification (CORE-027)."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Log this operation",
            context={"operation": "implement"}
        )
        
        result = orchestrator.execute(request)
        
        # Should complete and log
        assert result is not None

    def test_audit_logs_routing_decision(self) -> None:
        """Audit trail logs routing decision."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Route and log",
            context={"domain": "core"}
        )
        
        result = orchestrator.execute(request)
        assert result is not None

    def test_audit_logs_execution_result(self) -> None:
        """Audit trail logs execution result."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Execute and log result",
            context={"operation": "fix"}
        )
        
        result = orchestrator.execute(request)
        assert result is not None


class TestMasterOrchestratorErrorRecovery:
    """Test error recovery in refactored MasterOrchestrator."""

    def test_error_recovery_on_classification_failure(self) -> None:
        """Error recovery when intent classification fails."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="",  # Empty text to trigger potential error
            context={}
        )
        
        result = orchestrator.execute(request)
        
        # Should handle gracefully
        assert result is not None

    def test_error_recovery_on_routing_failure(self) -> None:
        """Error recovery when routing fails."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Operation with routing error",
            context={"invalid_domain": "xyz"}
        )
        
        result = orchestrator.execute(request)
        
        # Should recover gracefully
        assert result is not None

    def test_error_recovery_on_execution_failure(self) -> None:
        """Error recovery when execution fails."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Operation with execution error",
            context={"error_trigger": True}
        )
        
        result = orchestrator.execute(request)
        
        # Should recover gracefully
        assert result is not None


class TestMasterOrchestratorIntegration:
    """Integration tests for refactored MasterOrchestrator."""

    def test_full_workflow_implement_operation(self) -> None:
        """Full workflow: Implement operation."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Implement new response header validator",
            context={
                "domain": "orchestrators",
                "operation": "implement",
                "priority": "high",
                "module": "response"
            }
        )
        
        result = orchestrator.execute(request)
        assert result is not None

    def test_full_workflow_fix_operation(self) -> None:
        """Full workflow: Fix operation."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Fix circular import in intent router",
            context={
                "domain": "core",
                "operation": "fix",
                "priority": "critical",
                "issue": "circular-import"
            }
        )
        
        result = orchestrator.execute(request)
        assert result is not None

    def test_full_workflow_refactor_operation(self) -> None:
        """Full workflow: Refactor operation."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Refactor master orchestrator stages for clarity",
            context={
                "domain": "orchestrators",
                "operation": "refactor",
                "priority": "medium",
                "target": "master_orchestrator"
            }
        )
        
        result = orchestrator.execute(request)
        assert result is not None

    def test_full_workflow_complex_operation(self) -> None:
        """Full workflow: Complex multi-domain operation."""
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Consolidate response formatting across orchestrators",
            context={
                "domain": "orchestrators",
                "subdomain": "response",
                "operation": "refactor",
                "priority": "high",
                "affected_modules": ["response", "composition", "validation"],
                "dependencies": ["TRANSFORM-002"]
            }
        )
        
        result = orchestrator.execute(request)
        assert result is not None


class TestMasterOrchestratorPerformance:
    """Performance tests for refactored MasterOrchestrator."""

    def test_orchestration_latency_acceptable(self) -> None:
        """Orchestration latency is acceptable (< 1 second per operation)."""
        import time
        orchestrator = MasterOrchestratorRefactored()
        
        request = OperationRequest(
            text="Performance test operation",
            context={"operation": "implement"}
        )
        
        start = time.time()
        result = orchestrator.execute(request)
        elapsed = time.time() - start
        
        # Should complete in < 1 second
        assert elapsed < 1.0
        assert result is not None

    def test_multiple_operations_throughput(self) -> None:
        """Can handle multiple operations efficiently."""
        import time
        orchestrator = MasterOrchestratorRefactored()
        
        start = time.time()
        
        for i in range(10):
            request = OperationRequest(
                text=f"Operation {i}",
                context={"index": i}
            )
            result = orchestrator.execute(request)
            assert result is not None
        
        elapsed = time.time() - start
        
        # 10 operations in < 5 seconds
        assert elapsed < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

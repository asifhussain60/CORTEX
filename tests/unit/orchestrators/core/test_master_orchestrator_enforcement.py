"""
Integration tests for MasterOrchestrator + EnforcementOrchestrator (Phase 6D).

Tests AC-PHASE-6C-001 integration: Verify that MasterOrchestrator.execute_operation()
correctly invokes the 7-agent EnforcementOrchestrator and handles BLOCKED/WARNING/PASS
enforcement levels appropriately.

Test Coverage:
- BLOCKED operations return Err immediately
- WARNING operations log but continue
- PASS operations continue silently
- SCREAMING_CASE filenames blocked (CORE-028)
- Markdown summaries blocked (CORE-002)
- _v2 files blocked (CORE-035)
- >500 LOC operations blocked (CORE-001)
- >1000 token continuations warned (CORE-004)
- High turn counts warned (>20 turns)
- Slow operations warned (>10s duration)
- Enforcement not initialized continues (resilience)
- Audit trail metadata logged correctly
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from cortex.core.result import Ok, Err

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.orchestrators.core.enforcement_orchestrator import (
    EnforcementOrchestrator,
    EnforcementLevel,
    EnforcementResult
)


class TestMasterOrchestratorEnforcement:
    """Test suite for MasterOrchestrator + EnforcementOrchestrator integration."""

    @pytest.fixture
    def mock_logger(self):
        """Mock logger for audit trail verification."""
        logger = Mock()
        logger.log_operation_start = Mock()
        logger.log_operation_complete = Mock()
        return logger

    @pytest.fixture
    def mock_enforcement_orchestrator(self):
        """Mock EnforcementOrchestrator for controlled testing."""
        enforcement = Mock(spec=EnforcementOrchestrator)
        enforcement.agents = [Mock()] * 7  # 7 agents
        return enforcement

    @pytest.fixture
    def master_orchestrator(self, mock_logger):
        """Create MasterOrchestrator instance for testing."""
        # Mock dependencies to isolate enforcement testing
        with patch('cortex.orchestrators.core.master_orchestrator.GovernanceRegistry'), \
             patch('cortex.orchestrators.core.master_orchestrator.get_intent_router'), \
             patch('cortex.orchestrators.core.master_orchestrator.DoRApprovalGate'):
            
            orchestrator = MasterOrchestrator()
            orchestrator.logger = mock_logger
            return orchestrator

    # ═══════════════════════════════════════════════════════════════════════
    # BLOCKED Level Tests (Operations that should be blocked)
    # ═══════════════════════════════════════════════════════════════════════

    def test_blocked_operation_returns_error(self, master_orchestrator, mock_enforcement_orchestrator, mock_logger):
        """Test that BLOCKED enforcement level returns Err immediately."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=["CORE-001: Operation exceeds 500 LOC limit"],
                warnings=[],
                metadata={"agent": "IncrementalExecutionAgent"}
            )
        )
        
        parameters = {
            "estimated_loc": 750,
            "output_files": ["large_file.py"]
        }
        
        # Act
        result = master_orchestrator.execute_operation("IMPLEMENT_FEATURE", parameters)
        
        # Assert
        assert result.is_err(), "Expected Err result for BLOCKED operation"
        assert "Governance violation" in result.error
        assert "CORE-001" in result.error
        
        # Verify audit trail logged
        mock_logger.log_operation_complete.assert_called()
        call_args = mock_logger.log_operation_complete.call_args
        assert call_args[1]["ac_id"] == "AC-PHASE-6C-001"
        assert call_args[1]["operation"] == "GOVERNANCE_ENFORCEMENT_BLOCKED"
        assert call_args[1]["success"] is False

    def test_screaming_case_filename_blocked(self, master_orchestrator, mock_enforcement_orchestrator):
        """Test that SCREAMING_CASE filenames are blocked (CORE-028)."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=["CORE-028: SCREAMING_CASE filename detected: PLANNING_SUMMARY.md"],
                warnings=[],
                metadata={"agent": "FileNamingEnforcementAgent"}
            )
        )
        
        parameters = {
            "output_files": ["PLANNING_SUMMARY.md"],
            "target_file": "orchestrator.py"
        }
        
        # Act
        result = master_orchestrator.execute_operation("GENERATE_PLAN", parameters)
        
        # Assert
        assert result.is_err()
        assert "CORE-028" in result.error
        assert "SCREAMING_CASE" in result.error

    def test_markdown_summary_blocked(self, master_orchestrator, mock_enforcement_orchestrator):
        """Test that markdown summary files are blocked (CORE-002)."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=["CORE-002: Forbidden markdown artifact: deployment-summary.md"],
                warnings=[],
                metadata={"agent": "MarkdownSuppressionAgent"}
            )
        )
        
        parameters = {
            "output_files": ["deployment-summary.md"],
            "user_explicit_request": False
        }
        
        # Act
        result = master_orchestrator.execute_operation("DEPLOY_SYSTEM", parameters)
        
        # Assert
        assert result.is_err()
        assert "CORE-002" in result.error
        assert "deployment-summary.md" in result.error

    def test_v2_filename_blocked(self, master_orchestrator, mock_enforcement_orchestrator):
        """Test that _v2 versioned files are blocked (CORE-035)."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=["CORE-035: Versioned filename detected: orchestrator_v2.py"],
                warnings=[],
                metadata={"agent": "ArchitectureIntegrityAgent"}
            )
        )
        
        parameters = {
            "output_files": ["orchestrator_v2.py"],
            "target_file": "orchestrator.py"
        }
        
        # Act
        result = master_orchestrator.execute_operation("REFACTOR_CODE", parameters)
        
        # Assert
        assert result.is_err()
        assert "CORE-035" in result.error
        assert "_v2" in result.error

    def test_large_operation_blocked(self, master_orchestrator, mock_enforcement_orchestrator):
        """Test that >500 LOC operations are blocked (CORE-001)."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=["CORE-001: Operation exceeds 500 LOC limit (estimated: 650 LOC)"],
                warnings=[],
                metadata={"agent": "IncrementalExecutionAgent"}
            )
        )
        
        parameters = {
            "estimated_loc": 650,
            "output_files": ["large_module.py"]
        }
        
        # Act
        result = master_orchestrator.execute_operation("IMPLEMENT_MODULE", parameters)
        
        # Assert
        assert result.is_err()
        assert "CORE-001" in result.error
        assert "500 LOC" in result.error

    # ═══════════════════════════════════════════════════════════════════════
    # WARNING Level Tests (Operations that should continue with warnings)
    # ═══════════════════════════════════════════════════════════════════════

    def test_warning_operation_continues(self, master_orchestrator, mock_enforcement_orchestrator, mock_logger):
        """Test that WARNING enforcement level logs but continues execution."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        master_orchestrator._turn_number = 1
        
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.WARNING,
                violations=[],
                warnings=["CORE-004: High continuation token count (1200 tokens)"],
                metadata={"agent": "IncrementalExecutionAgent"}
            )
        )
        
        # Mock Stage 1 comprehension to avoid full execution
        with patch.object(master_orchestrator, 'interaction_orchestrator_with_challenges', None):
            parameters = {
                "continuation_tokens": 1200,
                "output_files": ["medium_file.py"]
            }
            
            # Act
            result = master_orchestrator.execute_operation("IMPLEMENT_FEATURE", parameters)
            
            # Assert - operation should continue (not return Err)
            # Note: May fail due to missing orchestrators, but shouldn't be blocked by enforcement
            # The key test is that we got past the enforcement gate
            
            # Verify warning was logged
            mock_logger.log_operation_complete.assert_called()
            call_args_list = [call[1] for call in mock_logger.log_operation_complete.call_args_list 
                             if call[1].get("operation") == "GOVERNANCE_ENFORCEMENT_WARNING"]
            assert len(call_args_list) > 0, "Expected WARNING to be logged"
            
            warning_log = call_args_list[0]
            assert warning_log["ac_id"] == "AC-PHASE-6C-001"
            assert warning_log["success"] is True
            assert "CORE-004" in str(warning_log["details"]["warnings"])

    def test_high_turn_count_warned(self, master_orchestrator, mock_enforcement_orchestrator, mock_logger):
        """Test that >20 turn operations are warned (CORE-038)."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        master_orchestrator._turn_number = 25
        
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.WARNING,
                violations=[],
                warnings=["CORE-038: High turn count (25 turns, limit: 20)"],
                metadata={"agent": "ArchitectureIntegrityAgent"}
            )
        )
        
        with patch.object(master_orchestrator, 'interaction_orchestrator_with_challenges', None):
            parameters = {"turn_count": 25}
            
            # Act
            result = master_orchestrator.execute_operation("LONG_OPERATION", parameters)
            
            # Assert - verify warning logged
            call_args_list = [call[1] for call in mock_logger.log_operation_complete.call_args_list 
                             if call[1].get("operation") == "GOVERNANCE_ENFORCEMENT_WARNING"]
            assert len(call_args_list) > 0
            
            warning_log = call_args_list[0]
            assert "CORE-038" in str(warning_log["details"]["warnings"])

    def test_slow_operation_warned(self, master_orchestrator, mock_enforcement_orchestrator, mock_logger):
        """Test that >10s operations are warned (CORE-039)."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        master_orchestrator._turn_number = 1
        
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.WARNING,
                violations=[],
                warnings=["CORE-039: Operation duration exceeds budget (15s, limit: 10s)"],
                metadata={"agent": "ArchitectureIntegrityAgent"}
            )
        )
        
        with patch.object(master_orchestrator, 'interaction_orchestrator_with_challenges', None):
            parameters = {"estimated_duration_seconds": 15}
            
            # Act
            result = master_orchestrator.execute_operation("SLOW_OPERATION", parameters)
            
            # Assert
            call_args_list = [call[1] for call in mock_logger.log_operation_complete.call_args_list 
                             if call[1].get("operation") == "GOVERNANCE_ENFORCEMENT_WARNING"]
            assert len(call_args_list) > 0
            
            warning_log = call_args_list[0]
            assert "CORE-039" in str(warning_log["details"]["warnings"])

    # ═══════════════════════════════════════════════════════════════════════
    # PASS Level Tests (Compliant operations)
    # ═══════════════════════════════════════════════════════════════════════

    def test_compliant_operation_passes(self, master_orchestrator, mock_enforcement_orchestrator, mock_logger):
        """Test that compliant operations pass through without blocking or warnings."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        master_orchestrator._turn_number = 1
        
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.PASS,
                violations=[],
                warnings=[],
                metadata={"agent": "EnforcementOrchestrator"}
            )
        )
        
        with patch.object(master_orchestrator, 'interaction_orchestrator_with_challenges', None):
            parameters = {
                "estimated_loc": 150,
                "continuation_tokens": 500,
                "output_files": ["clean_file.py"]
            }
            
            # Act
            result = master_orchestrator.execute_operation("IMPLEMENT_FEATURE", parameters)
            
            # Assert - should NOT have BLOCKED or WARNING logs for enforcement
            enforcement_logs = [call[1] for call in mock_logger.log_operation_complete.call_args_list 
                               if "GOVERNANCE_ENFORCEMENT" in call[1].get("operation", "")]
            
            # PASS should not log anything (continues silently)
            blocked_logs = [log for log in enforcement_logs if "BLOCKED" in log["operation"]]
            warning_logs = [log for log in enforcement_logs if "WARNING" in log["operation"]]
            
            assert len(blocked_logs) == 0, "PASS operations should not be blocked"
            assert len(warning_logs) == 0, "PASS operations should not have warnings"

    # ═══════════════════════════════════════════════════════════════════════
    # Resilience Tests (Enforcement system errors)
    # ═══════════════════════════════════════════════════════════════════════

    def test_enforcement_not_initialized_continues(self, master_orchestrator, mock_logger):
        """Test that operations continue if EnforcementOrchestrator is not initialized (resilience)."""
        # Arrange
        master_orchestrator._enforcement = None  # Not initialized
        master_orchestrator._turn_number = 1
        
        with patch.object(master_orchestrator, 'interaction_orchestrator_with_challenges', None):
            parameters = {
                "estimated_loc": 750,  # Would be blocked if enforcement was active
                "output_files": ["file.py"]
            }
            
            # Act
            result = master_orchestrator.execute_operation("IMPLEMENT_FEATURE", parameters)
            
            # Assert - should NOT be blocked (fail open)
            # Operation will fail for other reasons (missing orchestrators), but not blocked by enforcement
            enforcement_logs = [call[1] for call in mock_logger.log_operation_complete.call_args_list 
                               if "GOVERNANCE_ENFORCEMENT" in call[1].get("operation", "")]
            
            assert len(enforcement_logs) == 0, "No enforcement logs when orchestrator not initialized"

    def test_enforcement_error_continues(self, master_orchestrator, mock_enforcement_orchestrator, mock_logger):
        """Test that enforcement errors are logged but don't block operation (fail open)."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        master_orchestrator._turn_number = 1
        
        # Simulate enforcement system error
        mock_enforcement_orchestrator.validate_operation.return_value = Err("Enforcement system error")
        
        with patch.object(master_orchestrator, 'interaction_orchestrator_with_challenges', None):
            parameters = {"output_files": ["file.py"]}
            
            # Act
            result = master_orchestrator.execute_operation("IMPLEMENT_FEATURE", parameters)
            
            # Assert - error should be logged
            call_args_list = [call[1] for call in mock_logger.log_operation_complete.call_args_list 
                             if call[1].get("operation") == "GOVERNANCE_ENFORCEMENT_ERROR"]
            assert len(call_args_list) > 0, "Expected error to be logged"
            
            error_log = call_args_list[0]
            assert error_log["ac_id"] == "AC-PHASE-6C-001"
            assert error_log["success"] is False
            assert "Enforcement system error" in error_log["details"]["error"]

    # ═══════════════════════════════════════════════════════════════════════
    # Audit Trail Tests (Metadata logging)
    # ═══════════════════════════════════════════════════════════════════════

    def test_enforcement_metadata_logged(self, master_orchestrator, mock_enforcement_orchestrator, mock_logger):
        """Test that enforcement results include agent metadata in audit logs."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        master_orchestrator._turn_number = 1
        
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=["CORE-028: SCREAMING_CASE filename detected"],
                warnings=[],
                metadata={
                    "agent": "FileNamingEnforcementAgent",
                    "rule": "CORE-028",
                    "severity": "HIGH"
                }
            )
        )
        
        parameters = {"output_files": ["BAD_FILE.md"]}
        
        # Act
        result = master_orchestrator.execute_operation("CREATE_FILE", parameters)
        
        # Assert - verify metadata in audit log
        assert result.is_err()
        
        call_args = mock_logger.log_operation_complete.call_args
        assert call_args[1]["ac_id"] == "AC-PHASE-6C-001"
        assert "blocked_by_agents" in call_args[1]["details"]
        assert "FileNamingEnforcementAgent" in str(call_args[1]["details"]["blocked_by_agents"])

    def test_multiple_violations_blocked(self, master_orchestrator, mock_enforcement_orchestrator):
        """Test that multiple violations are all reported in the error message."""
        # Arrange
        master_orchestrator._enforcement = mock_enforcement_orchestrator
        
        mock_enforcement_orchestrator.validate_operation.return_value = Ok(
            EnforcementResult(
                level=EnforcementLevel.BLOCKED,
                violations=[
                    "CORE-001: Operation exceeds 500 LOC limit",
                    "CORE-028: SCREAMING_CASE filename detected",
                    "CORE-035: Versioned filename detected"
                ],
                warnings=[],
                metadata={"agent": "Multiple"}
            )
        )
        
        parameters = {
            "estimated_loc": 600,
            "output_files": ["MODULE_V2.py"]
        }
        
        # Act
        result = master_orchestrator.execute_operation("BAD_OPERATION", parameters)
        
        # Assert - all violations in error message
        assert result.is_err()
        error_msg = result.error
        assert "CORE-001" in error_msg
        assert "CORE-028" in error_msg
        assert "CORE-035" in error_msg


# ═════════════════════════════════════════════════════════════════════════
# Test Fixtures and Helpers
# ═════════════════════════════════════════════════════════════════════════

@pytest.fixture
def sample_operation_parameters():
    """Standard operation parameters for testing."""
    return {
        "intent": "IMPLEMENT_FEATURE",
        "output_files": ["feature.py"],
        "target_file": "module.py",
        "estimated_loc": 250,
        "continuation_tokens": 500,
        "turn_count": 5,
        "estimated_duration_seconds": 3,
        "user_explicit_request": False
    }

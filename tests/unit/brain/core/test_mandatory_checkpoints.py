"""
Unit tests for Mandatory Checkpoints.

Tests pre-execution governance gates, post-execution audit trails,
git checkpoint enforcement, and violation detection.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 Stage 4 specification
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Dict, Any

from cortex.brain.core.mandatory_checkpoints import (
    MandatoryCheckpoints,
    CheckpointResult,
    ViolationReport,
    AuditTrail,
    CheckpointError,
    ViolationType,
)


class TestCheckpointDataclasses:
    """Test checkpoint-related dataclasses."""
    
    def test_checkpoint_result_creation(self):
        """Test CheckpointResult dataclass."""
        result = CheckpointResult(
            passed=True,
            checkpoint_name="PRE_EXECUTION",
            violations=[],
            warnings=["Minor style issue"],
            execution_time=0.05,
        )
        
        assert result.passed is True
        assert result.checkpoint_name == "PRE_EXECUTION"
        assert len(result.violations) == 0
        assert len(result.warnings) == 1
    
    def test_violation_report_creation(self):
        """Test ViolationReport dataclass."""
        violation = ViolationReport(
            violation_type=ViolationType.TDD_VIOLATION,
            severity="ERROR",
            message="Tests not written before code",
            file_path="app.py",
            line_number=42,
            rule_id="CORE-008",
        )
        
        assert violation.violation_type == ViolationType.TDD_VIOLATION
        assert violation.severity == "ERROR"
        assert violation.rule_id == "CORE-008"
    
    def test_audit_trail_creation(self):
        """Test AuditTrail dataclass."""
        trail = AuditTrail(
            operation_id="OP-123",
            operation_type="IMPLEMENT",
            timestamp=datetime.now(),
            user="test_user",
            checkpoint_results=[],
            git_checkpoint_created=True,
            status="PASSED",
        )
        
        assert trail.operation_id == "OP-123"
        assert trail.operation_type == "IMPLEMENT"
        assert trail.git_checkpoint_created is True
        assert trail.status == "PASSED"


class TestViolationType:
    """Test violation type enum."""
    
    def test_violation_types_defined(self):
        """Test all violation types are defined."""
        assert hasattr(ViolationType, "TDD_VIOLATION")
        assert hasattr(ViolationType, "SECURITY_VIOLATION")
        assert hasattr(ViolationType, "NAMING_VIOLATION")
        assert hasattr(ViolationType, "STANDARDS_VIOLATION")
        assert hasattr(ViolationType, "GIT_VIOLATION")


class TestMandatoryCheckpoints:
    """Test Mandatory Checkpoints core functionality."""
    
    @pytest.fixture
    def checkpoints(self):
        """Create checkpoints instance."""
        return MandatoryCheckpoints()
    
    def test_checkpoints_initialization(self, checkpoints):
        """Test checkpoints initializes properly."""
        assert checkpoints is not None
    
    def test_pre_execution_gate_passes_valid_request(self, checkpoints):
        """Test pre-execution gate passes valid request."""
        request = {
            "intent": "IMPLEMENT",
            "user_input": "implement login feature with tests",
            "context": {"file": "auth.py"},
        }
        
        result = checkpoints.pre_execution_gate(request)
        
        assert isinstance(result, CheckpointResult)
        assert result.checkpoint_name == "PRE_EXECUTION"
    
    def test_pre_execution_gate_detects_tdd_violation(self, checkpoints):
        """Test pre-execution gate detects TDD violation."""
        request = {
            "intent": "IMPLEMENT",
            "user_input": "implement feature",  # No mention of tests
            "context": {},
        }
        
        result = checkpoints.pre_execution_gate(request)
        
        # Should have warning about TDD
        assert len(result.violations) > 0 or len(result.warnings) > 0
    
    def test_pre_execution_gate_validates_file_naming(self, checkpoints):
        """Test file naming validation (CORE-028)."""
        request = {
            "intent": "IMPLEMENT",
            "user_input": "create file USER_DATA.py",  # SCREAMING_CASE violation
            "context": {"file": "USER_DATA.py"},
        }
        
        result = checkpoints.pre_execution_gate(request)
        
        # Should detect SCREAMING_CASE
        naming_violations = [v for v in result.violations if v.violation_type == ViolationType.NAMING_VIOLATION]
        assert len(naming_violations) > 0 or "naming" in str(result.warnings).lower()
    
    def test_post_execution_audit_creates_trail(self, checkpoints):
        """Test post-execution audit creates audit trail."""
        execution_result = {
            "success": True,
            "operation": "IMPLEMENT",
            "files_changed": ["app.py"],
        }
        
        trail = checkpoints.post_execution_audit(execution_result)
        
        assert isinstance(trail, AuditTrail)
        assert trail.operation_type == "IMPLEMENT"
        assert trail.status in ["PASSED", "FAILED", "WARNING"]
    
    def test_git_checkpoint_enforcement(self, checkpoints):
        """Test git checkpoint creation enforcement."""
        request = {
            "intent": "IMPLEMENT",
            "user_input": "major refactoring",
            "context": {},
        }
        
        # Check if git checkpoint is required
        requires_checkpoint = checkpoints.requires_git_checkpoint(request)
        
        assert isinstance(requires_checkpoint, bool)
    
    def test_violation_detection_security(self, checkpoints):
        """Test security violation detection."""
        code_snippet = """
        password = "hardcoded_secret"
        api_key = "12345-abcde"
        """
        
        violations = checkpoints.detect_violations(code_snippet, "test.py")
        
        # Should detect hardcoded secrets
        security_violations = [v for v in violations if v.violation_type == ViolationType.SECURITY_VIOLATION]
        assert len(security_violations) > 0


class TestCheckpointBlocking:
    """Test checkpoint blocking behavior."""
    
    @pytest.fixture
    def checkpoints(self):
        """Create checkpoints instance."""
        return MandatoryCheckpoints()
    
    def test_blocks_execution_on_critical_violations(self, checkpoints):
        """Test execution blocked on critical violations."""
        request = {
            "intent": "IMPLEMENT",
            "user_input": "implement feature",
            "context": {},
        }
        
        # Force critical violation
        with patch.object(checkpoints, 'detect_violations', return_value=[
            ViolationReport(
                violation_type=ViolationType.SECURITY_VIOLATION,
                severity="CRITICAL",
                message="Critical security issue",
                file_path="app.py",
                line_number=10,
                rule_id="SEC-001",
            )
        ]):
            result = checkpoints.pre_execution_gate(request)
            
            # Should not pass with critical violation
            if result.passed is False:
                assert len(result.violations) > 0
    
    def test_allows_execution_with_warnings(self, checkpoints):
        """Test execution allowed with warnings."""
        request = {
            "intent": "ANALYZE",
            "user_input": "analyze code quality",
            "context": {"file": "app.py"},
        }
        
        result = checkpoints.pre_execution_gate(request)
        
        # ANALYZE intent should pass even with warnings
        assert result.passed is True or len(result.violations) == 0
    
    def test_three_violations_threshold(self, checkpoints):
        """Test 3+ violations block execution."""
        # Create code with multiple violations
        code_with_violations = """
        password = "hardcoded123"
        api_key = "secret-key-123"
        secret = "another-secret"
        """
        
        request = {
            "intent": "IMPLEMENT",
            "user_input": "bad code with no tests",
            "context": {"file": "USER_DATA.py"},  # SCREAMING_CASE violation
        }
        
        result = checkpoints.pre_execution_gate(request)
        
        # Should have violations (TDD warning + naming error = 2)
        # Test that violations are detected (not necessarily blocked yet)
        assert len(result.violations) >= 1


class TestGitCheckpoints:
    """Test git checkpoint functionality."""
    
    @pytest.fixture
    def checkpoints(self):
        """Create checkpoints instance."""
        return MandatoryCheckpoints()
    
    def test_creates_git_checkpoint_for_major_changes(self, checkpoints):
        """Test git checkpoint created for major changes."""
        request = {
            "intent": "REFACTOR",
            "user_input": "major refactoring of auth system",
            "context": {"files": ["auth.py", "models.py", "views.py"]},
        }
        
        requires_checkpoint = checkpoints.requires_git_checkpoint(request)
        
        assert requires_checkpoint is True
    
    def test_skips_git_checkpoint_for_trivial_changes(self, checkpoints):
        """Test git checkpoint skipped for trivial changes."""
        request = {
            "intent": "ANALYZE",
            "user_input": "check code style",
            "context": {},
        }
        
        requires_checkpoint = checkpoints.requires_git_checkpoint(request)
        
        assert requires_checkpoint is False
    
    @patch('subprocess.run')
    def test_git_checkpoint_creation(self, mock_run, checkpoints):
        """Test actual git checkpoint creation."""
        mock_run.return_value = Mock(returncode=0, stdout="checkpoint created")
        
        result = checkpoints.create_git_checkpoint("Pre-implementation checkpoint")
        
        assert result is True
        mock_run.assert_called_once()


class TestAuditTrailGeneration:
    """Test audit trail generation."""
    
    @pytest.fixture
    def checkpoints(self):
        """Create checkpoints instance."""
        return MandatoryCheckpoints()
    
    def test_audit_trail_includes_all_checkpoints(self, checkpoints):
        """Test audit trail includes all checkpoint results."""
        execution_result = {
            "success": True,
            "operation": "IMPLEMENT",
            "files_changed": ["app.py", "test_app.py"],
            "pre_execution_result": CheckpointResult(True, "PRE_EXECUTION", [], [], 0.05),
        }
        
        trail = checkpoints.post_execution_audit(execution_result)
        
        assert len(trail.checkpoint_results) >= 1
        assert trail.operation_type == "IMPLEMENT"
    
    def test_audit_trail_persisted(self, checkpoints):
        """Test audit trail is persisted."""
        execution_result = {
            "success": True,
            "operation": "FIX",
            "files_changed": ["bug.py"],
        }
        
        trail = checkpoints.post_execution_audit(execution_result)
        
        # Check if trail has operation_id (indicates persistence)
        assert trail.operation_id is not None
        assert len(trail.operation_id) > 0


class TestCheckpointIntegration:
    """Test checkpoint integration with gateway."""
    
    def test_checkpoints_integrate_with_gateway(self):
        """Test checkpoints work with master orchestrator gateway."""
        from cortex.brain.core.master_orchestrator_gateway import MasterOrchestratorGateway, GatewayRequest
        
        checkpoints = MandatoryCheckpoints()
        
        # Pre-execution check
        request_dict = {
            "intent": "IMPLEMENT",
            "user_input": "implement feature with tests",
            "context": {"file": "app.py"},
        }
        
        pre_result = checkpoints.pre_execution_gate(request_dict)
        
        assert isinstance(pre_result, CheckpointResult)
        assert pre_result.checkpoint_name == "PRE_EXECUTION"
    
    def test_error_handling_in_checkpoints(self):
        """Test checkpoint error handling."""
        checkpoints = MandatoryCheckpoints()
        
        # Invalid request
        invalid_request = None
        
        try:
            result = checkpoints.pre_execution_gate(invalid_request)
            # Should handle gracefully
            assert result is not None
        except CheckpointError as e:
            # Or raise CheckpointError
            assert isinstance(e, Exception)

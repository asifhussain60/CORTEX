"""
Integration tests for EdgeCaseValidator

Tests all edge case validations for CORTEX 3.0 unified planning system.

Author: Asif Hussain
Date: December 17, 2025
"""

import pytest
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta
from src.orchestration_3_0.core.edge_case_validator import (
    EdgeCaseValidator,
    ValidationSeverity,
    ValidationIssue,
    ValidationReport
)


@pytest.fixture
def temp_sessions_dir():
    """Create temporary sessions directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def validator(temp_sessions_dir):
    """Create EdgeCaseValidator instance."""
    return EdgeCaseValidator(
        sessions_dir=temp_sessions_dir,
        max_sessions=5,
        min_disk_space_gb=0.1,  # Low threshold for testing
        analysis_timeout=2,  # 2 seconds for testing
        session_expiry_hours=1,  # 1 hour for testing
        max_iterations=10
    )


class TestInputSanitization:
    """Test input sanitization (#6)."""
    
    def test_clean_input_passes(self, validator):
        """Clean input should pass validation."""
        issue = validator.validate_input_sanitization(
            "user-authentication-feature",
            "feature_name"
        )
        assert issue is None
    
    def test_eval_injection_detected(self, validator):
        """Eval injection should be detected."""
        issue = validator.validate_input_sanitization(
            "feature with eval(code)",
            "feature_name"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "code injection" in issue.message.lower()
    
    def test_import_injection_detected(self, validator):
        """Import injection should be detected."""
        issue = validator.validate_input_sanitization(
            "import os; os.system('rm -rf /')",
            "description"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
    
    def test_path_traversal_detected(self, validator):
        """Path traversal should be detected."""
        issue = validator.validate_input_sanitization(
            "../../../etc/passwd",
            "file_path"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL


class TestFilesystemSafeName:
    """Test filesystem-safe name validation (#5)."""
    
    def test_valid_name_passes(self, validator):
        """Valid filesystem-safe name should pass."""
        issue = validator.validate_filesystem_safe_name(
            "user-auth-feature",
            "feature_name"
        )
        assert issue is None
    
    def test_empty_name_fails(self, validator):
        """Empty name should fail."""
        issue = validator.validate_filesystem_safe_name("", "feature_name")
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "empty" in issue.message.lower()
    
    def test_special_chars_fail(self, validator):
        """Special characters should fail."""
        issue = validator.validate_filesystem_safe_name(
            "user@auth#feature",
            "feature_name"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "invalid characters" in issue.message.lower()
    
    def test_spaces_fail(self, validator):
        """Spaces should fail."""
        issue = validator.validate_filesystem_safe_name(
            "user auth feature",
            "feature_name"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
    
    def test_name_too_long_fails(self, validator):
        """Name over 100 chars should fail."""
        issue = validator.validate_filesystem_safe_name(
            "a" * 101,
            "feature_name"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "too long" in issue.message.lower()


class TestSessionFileLocking:
    """Test session file locking (#2)."""
    
    def test_lock_acquisition_succeeds(self, validator):
        """Lock acquisition should succeed."""
        acquired = validator.acquire_session_file_lock("session-001")
        assert acquired is True
        validator.release_session_file_lock("session-001")
    
    def test_concurrent_lock_fails(self, validator):
        """Concurrent lock on same session should fail."""
        # First lock succeeds
        acquired1 = validator.acquire_session_file_lock("session-001", timeout=0.1)
        assert acquired1 is True
        
        # Second lock should timeout
        acquired2 = validator.acquire_session_file_lock("session-001", timeout=0.1)
        assert acquired2 is False
        
        # Release first lock
        validator.release_session_file_lock("session-001")
        
        # Now second lock should succeed
        acquired3 = validator.acquire_session_file_lock("session-001")
        assert acquired3 is True
        validator.release_session_file_lock("session-001")
    
    def test_multiple_sessions_can_lock(self, validator):
        """Different sessions should be able to lock concurrently."""
        acquired1 = validator.acquire_session_file_lock("session-001")
        acquired2 = validator.acquire_session_file_lock("session-002")
        
        assert acquired1 is True
        assert acquired2 is True
        
        validator.release_session_file_lock("session-001")
        validator.release_session_file_lock("session-002")


class TestRollbackSafety:
    """Test rollback safety for plan promotion (#9)."""
    
    def test_missing_temp_plan_fails(self, validator, temp_sessions_dir):
        """Missing temp plan should fail."""
        issue = validator.validate_rollback_safety(
            plan_id="test-plan",
            temp_plan_path=temp_sessions_dir / "nonexistent",
            permanent_plan_path=temp_sessions_dir / "permanent"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "not found" in issue.message.lower()
    
    def test_existing_permanent_plan_warns(self, validator, temp_sessions_dir):
        """Existing permanent plan should warn."""
        # Create temp plan
        temp_plan = temp_sessions_dir / "temp"
        temp_plan.mkdir()
        
        # Create permanent plan
        permanent_plan = temp_sessions_dir / "permanent"
        permanent_plan.mkdir()
        
        issue = validator.validate_rollback_safety(
            plan_id="test-plan",
            temp_plan_path=temp_plan,
            permanent_plan_path=permanent_plan
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.WARNING
        assert "already exists" in issue.message.lower()
        assert issue.auto_fixable is True
    
    def test_clean_promotion_passes(self, validator, temp_sessions_dir):
        """Clean promotion should pass."""
        # Create temp plan
        temp_plan = temp_sessions_dir / "temp"
        temp_plan.mkdir()
        
        # Permanent plan doesn't exist
        permanent_plan = temp_sessions_dir / "permanent"
        
        issue = validator.validate_rollback_safety(
            plan_id="test-plan",
            temp_plan_path=temp_plan,
            permanent_plan_path=permanent_plan
        )
        assert issue is None


class TestAnalysisTimeout:
    """Test analysis timeout validation (#11, #12)."""
    
    def test_within_timeout_passes(self, validator):
        """Analysis within timeout should pass."""
        issue = validator.validate_analysis_timeout("AST", 1.0)
        assert issue is None
    
    def test_exceeding_timeout_fails(self, validator):
        """Analysis exceeding timeout should fail."""
        issue = validator.validate_analysis_timeout("AST", 3.0)
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "exceeded timeout" in issue.message.lower()
    
    def test_approaching_timeout_warns(self, validator):
        """Analysis approaching timeout should warn."""
        # 80% of timeout (1.6s out of 2s)
        issue = validator.validate_analysis_timeout("Lens", 1.6)
        assert issue is not None
        assert issue.severity == ValidationSeverity.WARNING
        assert "approaching timeout" in issue.message.lower()


class TestIdempotency:
    """Test idempotency validation (#17)."""
    
    def test_correct_state_passes(self, validator):
        """Correct state should pass."""
        issue = validator.validate_idempotency(
            operation="approve",
            plan_id="plan-001",
            expected_state="drafting",
            current_state="drafting"
        )
        assert issue is None
    
    def test_incorrect_state_fails(self, validator):
        """Incorrect state should fail."""
        issue = validator.validate_idempotency(
            operation="approve",
            plan_id="plan-001",
            expected_state="drafting",
            current_state="approved"
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "expected state" in issue.message.lower()


class TestMaxIterations:
    """Test max iterations validation (#10)."""
    
    def test_within_limit_passes(self, validator):
        """Iteration within limit should pass."""
        issue = validator.validate_max_iterations(5)
        assert issue is None
    
    def test_exceeding_limit_fails(self, validator):
        """Iteration exceeding limit should fail."""
        issue = validator.validate_max_iterations(11)
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "exceeded" in issue.message.lower()
    
    def test_approaching_limit_warns(self, validator):
        """Iteration approaching limit should warn."""
        # 80% of limit (8 out of 10)
        issue = validator.validate_max_iterations(8)
        assert issue is not None
        assert issue.severity == ValidationSeverity.WARNING
        assert "approaching" in issue.message.lower()


class TestConcurrentSessions:
    """Test concurrent session validation (#1)."""
    
    def test_single_session_passes(self, validator):
        """Single session should pass."""
        issue = validator.validate_concurrent_sessions(["session-001"])
        assert issue is None
    
    def test_multiple_sessions_warns(self, validator):
        """Multiple sessions should warn."""
        issue = validator.validate_concurrent_sessions(
            ["session-001", "session-002", "session-003"]
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.WARNING
        assert "concurrent" in issue.message.lower()


class TestStaleSessionCleanup:
    """Test stale session cleanup (#8)."""
    
    def test_cleanup_stale_sessions(self, validator, temp_sessions_dir):
        """Stale sessions should be cleaned up."""
        import json
        
        # Create sessions file with stale session
        sessions_file = temp_sessions_dir / "active-sessions.json"
        
        old_timestamp = (datetime.now() - timedelta(hours=25)).isoformat()
        recent_timestamp = datetime.now().isoformat()
        
        sessions_data = {
            "session-001": {
                "session_id": "session-001",
                "plan_id": "plan-001",
                "created_at": old_timestamp,
                "last_updated": old_timestamp,
                "status": "drafting"
            },
            "session-002": {
                "session_id": "session-002",
                "plan_id": "plan-002",
                "created_at": recent_timestamp,
                "last_updated": recent_timestamp,
                "status": "drafting"
            }
        }
        
        sessions_file.write_text(json.dumps(sessions_data, indent=2))
        
        # Run cleanup
        cleaned = validator.cleanup_stale_sessions()
        
        # Should have cleaned session-001 but not session-002
        assert "session-001" in cleaned
        assert len(cleaned) == 1
        
        # Check sessions file was updated
        updated_data = json.loads(sessions_file.read_text())
        assert "session-001" not in updated_data
        assert "session-002" in updated_data


class TestMaxSessionsLimit:
    """Test max sessions limit (#15)."""
    
    def test_within_limit_passes(self, validator):
        """Within limit should pass."""
        issue = validator.validate_max_sessions_limit(3)
        assert issue is None
    
    def test_at_limit_fails(self, validator):
        """At limit should fail."""
        issue = validator.validate_max_sessions_limit(5)
        assert issue is not None
        assert issue.severity == ValidationSeverity.CRITICAL
        assert "limit reached" in issue.message.lower()
    
    def test_approaching_limit_warns(self, validator):
        """Approaching limit should warn."""
        # 80% of limit (4 out of 5)
        issue = validator.validate_max_sessions_limit(4)
        assert issue is not None
        assert issue.severity == ValidationSeverity.WARNING
        assert "approaching" in issue.message.lower()


class TestSessionExpiry:
    """Test session expiry validation (#19)."""
    
    def test_recent_session_passes(self, validator):
        """Recent session should pass."""
        created_at = datetime.now() - timedelta(minutes=30)
        issue = validator.validate_session_expiry(created_at)
        assert issue is None
    
    def test_expired_session_warns(self, validator):
        """Expired session should warn."""
        created_at = datetime.now() - timedelta(hours=25)
        issue = validator.validate_session_expiry(created_at)
        assert issue is not None
        assert issue.severity == ValidationSeverity.WARNING
        assert "expired" in issue.message.lower()
    
    def test_expiring_soon_info(self, validator):
        """Session expiring soon should info."""
        # 85% of expiry (51 minutes out of 60)
        created_at = datetime.now() - timedelta(minutes=51)
        issue = validator.validate_session_expiry(created_at)
        assert issue is not None
        assert issue.severity == ValidationSeverity.INFO
        assert "expiring soon" in issue.message.lower()


class TestComplexityAnalysis:
    """Test complexity analysis validation (#20)."""
    
    def test_matching_complexity_passes(self, validator):
        """Matching complexity should pass."""
        issue = validator.validate_complexity_analysis(
            feature_description="A feature with moderate complexity" * 10,
            acceptance_criteria_count=7,
            estimated_tier=3
        )
        assert issue is None
    
    def test_mismatched_complexity_info(self, validator):
        """Significantly mismatched complexity should provide info."""
        # Large description (>500 chars) but low tier
        issue = validator.validate_complexity_analysis(
            feature_description="x" * 600,
            acceptance_criteria_count=12,
            estimated_tier=1
        )
        assert issue is not None
        assert issue.severity == ValidationSeverity.INFO
        assert "may not match" in issue.message.lower()


class TestProgressCallback:
    """Test progress callback (#22)."""
    
    def test_progress_callback_invocable(self, validator):
        """Progress callback should be invocable."""
        callback = validator.create_progress_callback(
            operation="Test Operation",
            total_steps=5
        )
        
        # Should not raise exception
        callback(1, "Step 1 complete")
        callback(2, "Step 2 complete")
        callback(5, "All steps complete")


class TestComprehensiveValidation:
    """Test comprehensive validation workflows."""
    
    def test_planning_request_validation_clean(self, validator):
        """Clean planning request should pass."""
        report = validator.validate_planning_request(
            feature_name="user-authentication",
            feature_description="Implement user authentication with OAuth2 support" * 3,
            acceptance_criteria=["Login works", "Logout works", "Token refresh works"],
            active_sessions=[],
            current_session_count=1
        )
        
        assert report.passed is True
        assert len(report.critical_issues) == 0
    
    def test_planning_request_validation_with_issues(self, validator):
        """Planning request with issues should fail."""
        report = validator.validate_planning_request(
            feature_name="user auth!@#",  # Invalid chars
            feature_description="Short",  # Too short for injection check
            acceptance_criteria=["Test"],
            active_sessions=["s1", "s2"],  # Concurrent sessions
            current_session_count=5  # At limit
        )
        
        assert report.passed is False
        assert len(report.critical_issues) >= 1  # Filesystem safety
        assert len(report.warnings) >= 1  # Concurrent sessions or max sessions
    
    def test_session_operation_validation_clean(self, validator):
        """Clean session operation should pass."""
        report = validator.validate_session_operation(
            operation="update",
            session_id="session-001",
            session_created_at=datetime.now() - timedelta(minutes=30),
            current_iteration=3,
            expected_state="drafting",
            current_state="drafting"
        )
        
        assert report.passed is True
        assert len(report.critical_issues) == 0
    
    def test_session_operation_validation_with_issues(self, validator):
        """Session operation with issues should fail."""
        report = validator.validate_session_operation(
            operation="approve",
            session_id="session-001",
            session_created_at=datetime.now() - timedelta(hours=25),  # Expired
            current_iteration=11,  # Over limit
            expected_state="drafting",
            current_state="approved"  # Wrong state
        )
        
        assert report.passed is False
        assert len(report.critical_issues) >= 2  # State + iterations
        assert len(report.warnings) >= 1  # Expiry


class TestValidationReport:
    """Test ValidationReport helper methods."""
    
    def test_has_blocking_issues(self, validator):
        """Test has_blocking_issues method."""
        report = ValidationReport(
            passed=False,
            critical_issues=[
                ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="test",
                    message="Test issue"
                )
            ],
            warnings=[],
            info=[]
        )
        
        assert report.has_blocking_issues() is True
        assert report.passed is False
    
    def test_get_summary(self, validator):
        """Test get_summary method."""
        report = ValidationReport(
            passed=False,
            critical_issues=[
                ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="test",
                    message="Critical issue"
                )
            ],
            warnings=[
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="test",
                    message="Warning issue"
                )
            ],
            info=[]
        )
        
        summary = report.get_summary()
        assert "1 critical" in summary
        assert "1 warning" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

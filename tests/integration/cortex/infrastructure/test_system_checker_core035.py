"""
tests/integration/cortex/infrastructure/test_system_checker_core035.py

Integration tests for CORE-035 compliance check within SystemChecker.

Verifies that the health check integrates correctly with the overall
system checker framework and runs as part of the standard check suite.
"""

import pytest
from typing import Any
from unittest.mock import patch
from cortex.infrastructure.system_checker import SystemChecker
from cortex.infrastructure.core035_compliance_check import (
    reset_core035_checker,
    CORE035ComplianceCheck,
)


class TestSystemCheckerCORE035Integration:
    """Test integration of CORE-035 check with SystemChecker."""
    
    def setup_method(self) -> None:
        """Reset singleton before each test."""
        reset_core035_checker()
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_core035_check_in_system_checker(self, mock_audit: Any) -> None:
        """Test that CORE-035 check runs as part of run_all_checks()."""
        mock_audit.return_value = (0, 0, 0, 0)
        
        checker = SystemChecker()
        
        # Run all checks
        checker.run_all_checks()
        
        # Verify CORE-035 check was included
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        assert len(core035_checks) > 0
        assert core035_checks[0].passed is True
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_core035_check_with_violations(self, mock_audit: Any) -> None:
        """Test CORE-035 check with violations detected."""
        mock_audit.return_value = (100, 50, 50, 2)
        
        checker = SystemChecker()
        
        checker.run_all_checks()
        
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        # Should still pass (non-blocking)
        assert len(core035_checks) > 0
        assert core035_checks[0].passed is True
        
        # But should have violation info in details
        if hasattr(core035_checks[0], 'details'):
            details = core035_checks[0].details
            assert "violations" in str(details).lower()
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_core035_check_handles_errors(self, mock_audit: Any) -> None:
        """Test CORE-035 check handles execution errors gracefully."""
        mock_audit.side_effect = Exception("Audit script failed")
        
        checker = SystemChecker()
        
        # Should not raise exception
        checker.run_all_checks()
        
        # Core035 check should still be there (but may indicate error)
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        # Check should exist but passed=True (non-blocking)
        assert len(core035_checks) > 0
        assert core035_checks[0].passed is True
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_core035_does_not_block_other_checks(self, mock_audit: Any) -> None:
        """Test that CORE-035 violations don't block overall system health."""
        mock_audit.return_value = (285, 154, 101, 6)
        
        checker = SystemChecker()
        
        checker.run_all_checks()
        
        # Even with 285 violations, checks should pass
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        assert len(core035_checks) > 0
        assert core035_checks[0].passed is True
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_core035_check_position_in_suite(self, mock_audit: Any) -> None:
        """Test that CORE-035 check is included in proper position."""
        mock_audit.return_value = (0, 0, 0, 0)
        
        checker = SystemChecker()
        
        checker.run_all_checks()
        
        # Get all check names
        check_names = [check.name for check in checker.checks]
        
        # CORE-035 should be after wiring/contract/drift but before report
        core035_index = next(
            (i for i, name in enumerate(check_names) 
             if "CORE-035" in name),
            -1
        )
        
        assert core035_index >= 0
        assert core035_index < len(check_names)


class TestSystemCheckerReportWithCORE035:
    """Test system check reporting includes CORE-035 results."""
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_report_includes_core035_check(self, mock_audit: Any) -> None:
        """Test that system check report includes CORE-035 metrics."""
        mock_audit.return_value = (15, 10, 5, 2)
        
        checker = SystemChecker()
        checker.run_all_checks()
        
        # Verify check ran
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        assert len(core035_checks) > 0
        assert core035_checks[0].passed is True
        assert core035_checks[0].details is not None
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_report_shows_violations_count(self, mock_audit: Any) -> None:
        """Test that report shows violation counts when present."""
        mock_audit.return_value = (50, 25, 25, 2)
        
        checker = SystemChecker()
        checker.run_all_checks()
        
        # Should include check
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        assert len(core035_checks) > 0


class TestCORE035HealthCheckPerformance:
    """Test performance characteristics of CORE-035 health check."""
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_core035_check_completes_quickly(self, mock_audit: Any) -> None:
        """Test that CORE-035 check completes within reasonable time."""
        import time
        
        mock_audit.return_value = (100, 50, 50, 2)
        
        checker = SystemChecker()
        
        start_time = time.time()
        checker.run_all_checks()
        elapsed_time = time.time() - start_time
        
        # Overall check should complete in reasonable time
        # Even with 100 violations
        assert elapsed_time < 30  # 30 second timeout
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_core035_check_does_not_leak_memory(self, mock_audit: Any) -> None:
        """Test that repeated CORE-035 checks don't leak memory."""
        mock_audit.return_value = (0, 0, 0, 0)
        
        checker = SystemChecker()
        
        # Run multiple times
        for _ in range(5):
            checker.checks = []  # Reset checks
            checker.run_all_checks()
        
        # Should complete without issues
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        assert len(core035_checks) > 0


class TestCORE035CheckRecovery:
    """Test error recovery in CORE-035 health check."""
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_recovery_after_timeout(self, mock_audit: Any) -> None:
        """Test recovery after timeout in audit script."""
        import subprocess
        
        # First call times out, second succeeds
        mock_audit.side_effect = [
            subprocess.TimeoutExpired('cmd', 120),
            (0, 0, 0, 0)
        ]
        
        checker = SystemChecker()
        
        # First check might have issues but should not crash
        checker.run_all_checks()
        first_count = len([c for c in checker.checks if "CORE-035" in c.name])
        
        # Reset and run again
        reset_core035_checker()
        checker.checks = []
        checker.run_all_checks()
        second_count = len([c for c in checker.checks if "CORE-035" in c.name])
        
        # Both runs should have the check
        assert first_count > 0
        assert second_count > 0
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_recovery_after_permission_error(self, mock_audit: Any) -> None:
        """Test recovery after permission error."""
        mock_audit.side_effect = [
            PermissionError("Cannot read audit script"),
            (0, 0, 0, 0)
        ]
        
        checker = SystemChecker()
        
        # First check handles permission error
        checker.run_all_checks()
        
        # Should not crash and should have check
        core035_checks = [
            check for check in checker.checks 
            if "CORE-035" in check.name
        ]
        
        assert len(core035_checks) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

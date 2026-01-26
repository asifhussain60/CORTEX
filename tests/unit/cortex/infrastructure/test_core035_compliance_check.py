"""
tests/unit/cortex/infrastructure/test_core035_compliance_check.py

Unit tests for CORE-035 compliance health check.

Tests the detection, baseline tracking, and audit trail logging
of duplication violations.
"""

import pytest
import tempfile
import json
import subprocess
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch
from cortex.infrastructure.core035_compliance_check import (
    CORE035ComplianceCheck,
    CORE035ComplianceStatus,
    get_core035_checker,
    reset_core035_checker,
)


class TestCORE035ComplianceStatus:
    """Test CORE035ComplianceStatus dataclass."""
    
    def test_status_creation(self):
        """Test creating compliance status."""
        status = CORE035ComplianceStatus(
            violations_count=5,
            duplicate_classes=2,
            duplicate_functions=3,
            message="Test message",
        )
        
        assert status.violations_count == 5
        assert status.duplicate_classes == 2
        assert status.duplicate_functions == 3
        assert status.message == "Test message"
        assert status.healthy is True
    
    def test_to_dict(self):
        """Test converting status to dictionary."""
        status = CORE035ComplianceStatus(
            violations_count=10,
            duplicate_classes=4,
            duplicate_functions=6,
        )
        
        result = status.to_dict()
        
        assert isinstance(result, dict)
        assert result["violations_count"] == 10
        assert result["duplicate_classes"] == 4
        assert result["duplicate_functions"] == 6


class TestCORE035ComplianceCheck:
    """Test CORE035ComplianceCheck class."""
    
    def test_initialization(self):
        """Test checker initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            checker = CORE035ComplianceCheck(repo_root=repo_root)
            
            assert checker.repo_root == repo_root
            assert checker.audit_script == repo_root / "scripts" / "duplication_audit.py"
    
    def test_baseline_loading_nonexistent(self):
        """Test loading baseline when file doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            checker = CORE035ComplianceCheck(repo_root=repo_root)
            
            # Should return default baseline
            assert checker.baseline["violations_count"] == 0
            assert checker.baseline["duplicate_classes"] == 0
    
    def test_baseline_loading_existing(self):
        """Test loading baseline from existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            baseline_file = repo_root / ".cortex" / "core035_baseline.json"
            baseline_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create baseline file
            test_baseline = {
                "violations_count": 100,
                "duplicate_classes": 50,
                "duplicate_functions": 50,
                "timestamp": 0,
            }
            with open(baseline_file, 'w') as f:
                json.dump(test_baseline, f)
            
            checker = CORE035ComplianceCheck(repo_root=repo_root, baseline_file=baseline_file)
            
            assert checker.baseline["violations_count"] == 100
            assert checker.baseline["duplicate_classes"] == 50
    
    def test_compare_to_baseline_improved(self) -> None:
        """Test baseline comparison when improved."""
        checker = CORE035ComplianceCheck()
        checker.baseline = {"violations_count": 100}
        
        # noinspection PyProtectedMember
        result = checker._compare_to_baseline(50, 100)
        
        assert result == "improved"
    
    def test_compare_to_baseline_stable(self) -> None:
        """Test baseline comparison when stable."""
        checker = CORE035ComplianceCheck()
        checker.baseline = {"violations_count": 100}
        
        # noinspection PyProtectedMember
        result = checker._compare_to_baseline(100, 100)
        
        assert result == "stable"
    
    def test_compare_to_baseline_degraded(self) -> None:
        """Test baseline comparison when degraded."""
        checker = CORE035ComplianceCheck()
        checker.baseline = {"violations_count": 100}
        
        # noinspection PyProtectedMember
        result = checker._compare_to_baseline(150, 100)
        
        assert result == "degraded"
    
    @patch('subprocess.run')
    def test_audit_script_missing(self, mock_run: Any) -> None:
        """Test handling when audit script is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            checker = CORE035ComplianceCheck(repo_root=repo_root)
            
            # noinspection PyProtectedMember
            violations, classes, funcs, multi_path = checker._run_duplication_audit()
            
            assert violations == 0
            assert classes == 0
            assert funcs == 0
            assert multi_path == 0
    
    @patch('subprocess.run')
    def test_audit_script_execution(self, mock_run: Any) -> None:
        """Test audit script execution and parsing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            audit_script = repo_root / "scripts" / "duplication_audit.py"
            audit_script.parent.mkdir(parents=True, exist_ok=True)
            audit_script.touch()
            
            # Mock output with violations
            mock_output = """
            ❌ CLASS: ComplexityLevel
            Locations: 8 implementations found
            ❌ CLASS: SeverityLevel
            Locations: 5 implementations found
            ❌ FUNCTION: validate_schema()
            Locations: 2 implementations found
            """
            
            mock_run.return_value = Mock(
                returncode=0,
                stdout=mock_output,
                stderr=""
            )
            
            checker = CORE035ComplianceCheck(repo_root=repo_root)
            # noinspection PyProtectedMember
            violations, classes, funcs, _ = checker._run_duplication_audit()
            
            assert violations == 3  # 2 classes + 1 function
            assert classes == 2
            assert funcs == 1
    
    @patch('subprocess.run')
    def test_audit_timeout(self, mock_run: Any) -> None:
        """Test handling of audit script timeout."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            audit_script = repo_root / "scripts" / "duplication_audit.py"
            audit_script.parent.mkdir(parents=True, exist_ok=True)
            audit_script.touch()
            
            mock_run.side_effect = subprocess.TimeoutExpired('cmd', 120)
            
            checker = CORE035ComplianceCheck(repo_root=repo_root)
            # noinspection PyProtectedMember
            violations, classes, funcs, _ = checker._run_duplication_audit()
            
            assert violations == 0
            assert classes == 0
            assert funcs == 0
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_check_compliant(self, mock_audit: Any) -> None:
        """Test check when fully compliant."""
        mock_audit.return_value = (0, 0, 0, 0)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            checker = CORE035ComplianceCheck(repo_root=repo_root)
            status = checker.check()
            
            assert status.violations_count == 0
            assert status.duplicate_classes == 0
            assert status.healthy is True
            assert "COMPLIANT" in status.message
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_check_with_violations(self, mock_audit: Any) -> None:
        """Test check when violations found."""
        mock_audit.return_value = (15, 10, 5, 2)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            checker = CORE035ComplianceCheck(repo_root=repo_root)
            status = checker.check()
            
            assert status.violations_count == 15
            assert status.duplicate_classes == 10
            assert status.duplicate_functions == 5
            assert status.multi_path_orchestrators == 2
            assert status.healthy is True  # Non-blocking
            assert "violations detected" in status.message.lower()


class TestSingletonPattern:
    """Test singleton pattern for health check integration."""
    
    def test_get_checker_singleton(self):
        """Test getting singleton checker."""
        reset_core035_checker()
        
        checker1 = get_core035_checker()
        checker2 = get_core035_checker()
        
        assert checker1 is checker2
    
    def test_reset_checker(self):
        """Test resetting singleton."""
        reset_core035_checker()
        checker1 = get_core035_checker()
        
        reset_core035_checker()
        checker2 = get_core035_checker()
        
        assert checker1 is not checker2


class TestHealthCheckIntegration:
    """Test integration with system health check."""
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_health_check_no_violations(self, mock_audit: Any) -> None:
        """Test health check integration with no violations."""
        mock_audit.return_value = (0, 0, 0, 0)
        reset_core035_checker()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            checker = get_core035_checker(repo_root)
            status = checker.check()
            
            # Health check should always be healthy (non-blocking)
            assert status.healthy is True
            assert status.violations_count == 0
    
    @patch.object(CORE035ComplianceCheck, '_run_duplication_audit')
    def test_health_check_with_violations(self, mock_audit: Any) -> None:
        """Test health check integration with violations."""
        mock_audit.return_value = (285, 154, 101, 6)
        reset_core035_checker()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            checker = get_core035_checker(repo_root)
            status = checker.check()
            
            # Still healthy (non-blocking), but violations logged
            assert status.healthy is True
            assert status.violations_count == 285
            assert status.duplicate_classes == 154
            assert status.duplicate_functions == 101
            assert status.multi_path_orchestrators == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

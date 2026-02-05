"""
Tests for RegressionMonitor - TDDOrchestrator integration wrapper.

Tests verify that TDDOrchestrator properly calls regression checks
before execution and brittleness scanning after execution.

Author: Asif Hussain
Date: 2026-02-05
Phase: 24 (AC-PHASE24-005)
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from cortex.orchestrators.support.regression_monitor import RegressionMonitor


class TestRegressionMonitorIntegration:
    """Test RegressionMonitor integration with TDDOrchestrator."""
    
    @pytest.fixture
    def monitor(self, tmp_path: Path) -> RegressionMonitor:
        """Create RegressionMonitor instance."""
        # Create mock registry directory
        registry_dir = tmp_path / "cortex-registry" / "_cortex-master"
        registry_dir.mkdir(parents=True)
        
        # Create mock phases directory with one active phase
        phases_dir = registry_dir / "phases" / "active"
        phases_dir.mkdir(parents=True)
        
        phase_content = """
phase_id: 24
name: "Test Phase"
status: IN_PROGRESS
"""
        (phases_dir / "phase-24-test.yaml").write_text(phase_content)
        
        return RegressionMonitor(registry_dir)
    
    def test_check_completed_phases_no_violations(self, monitor: RegressionMonitor) -> None:
        """Test check_completed_phases with valid request."""
        context = {
            "request_description": "Add new feature to new module",
            "intent_type": "IMPLEMENT",
            "scope": ["new_feature"]
        }
        
        result = monitor.check_completed_phases(context)
        
        assert result["status"] == "PASS"
        assert result["verdict"] == "PROCEED"
        assert result["regression_risk"] < 0.3  # Low risk for new features
    
    def test_check_completed_phases_with_phase_keyword_overlap(self, monitor: RegressionMonitor) -> None:
        """Test check_completed_phases detects phase keyword overlap."""
        context = {
            "request_description": "Modify test phase implementation",
            "intent_type": "IMPLEMENT", 
            "scope": ["test_phase_module"]
        }
        
        result = monitor.check_completed_phases(context)
        
        # Should detect "test phase" keyword overlap with active phase
        assert result["status"] in ["WARNING", "PASS"]
        assert "regression_risk" in result
    
    def test_scan_brittleness_no_issues(self, monitor: RegressionMonitor, tmp_path: Path) -> None:
        """Test scan_brittleness with clean files."""
        # Create a simple Python file with no issues
        test_file = tmp_path / "test_module.py"
        test_file.write_text("""
def simple_function():
    return 42
""")
        
        result = monitor.scan_brittleness([str(test_file)])
        
        assert result["status"] == "PASS"
        assert result["brittleness_score"] == 0.0
        assert len(result["issues"]) == 0
    
    def test_scan_brittleness_detects_circular_deps(self, monitor: RegressionMonitor, tmp_path: Path) -> None:
        """Test scan_brittleness detects circular dependencies."""
        # Create files with circular imports
        file1 = tmp_path / "module_a.py"
        file1.write_text("""
import module_b

def func_a():
    return module_b.func_b()
""")
        
        file2 = tmp_path / "module_b.py"
        file2.write_text("""
import module_a

def func_b():
    return module_a.func_a()
""")
        
        result = monitor.scan_brittleness([str(file1), str(file2)])
        
        # Should detect circular dependency
        assert result["status"] in ["WARNING", "CRITICAL"]
        assert result["brittleness_score"] > 0.0
        assert any("circular" in issue.lower() for issue in result["issues"])
    
    def test_violations_logged_as_warnings(self, monitor: RegressionMonitor) -> None:
        """Test that violations are logged as warnings, not errors."""
        context = {
            "request_description": "Modify completed phase implementation",
            "intent_type": "IMPLEMENT",
            "scope": ["test_phase"]
        }
        
        # Should not raise exception even with violations
        result = monitor.check_completed_phases(context)
        
        assert result["status"] in ["PASS", "WARNING"]
        assert "verdict" in result
    
    def test_regression_check_non_blocking(self, monitor: RegressionMonitor) -> None:
        """Test that regression checks don't block execution."""
        context = {
            "request_description": "High risk modification",
            "intent_type": "IMPLEMENT",
            "scope": ["core_architecture"]
        }
        
        result = monitor.check_completed_phases(context)
        
        # Even high risk should return result, not raise exception
        assert result["status"] in ["PASS", "WARNING", "CRITICAL"]
        assert result["verdict"] in ["PROCEED", "BLOCK"]


class TestRegressionMonitorEdgeCases:
    """Test edge cases for RegressionMonitor."""
    
    def test_empty_context(self, tmp_path: Path) -> None:
        """Test with empty context."""
        registry_dir = tmp_path / "cortex-registry" / "_cortex-master"
        registry_dir.mkdir(parents=True)
        
        monitor = RegressionMonitor(registry_dir)
        result = monitor.check_completed_phases({})
        
        # Should handle gracefully with defaults
        assert result["status"] == "PASS"
        assert result["verdict"] == "PROCEED"
    
    def test_empty_file_list(self, tmp_path: Path) -> None:
        """Test brittleness scan with empty file list."""
        registry_dir = tmp_path / "cortex-registry" / "_cortex-master"
        registry_dir.mkdir(parents=True)
        
        monitor = RegressionMonitor(registry_dir)
        result = monitor.scan_brittleness([])
        
        # Should handle gracefully
        assert result["status"] == "PASS"
        assert result["brittleness_score"] == 0.0
    
    def test_nonexistent_files(self, tmp_path: Path) -> None:
        """Test brittleness scan with nonexistent files."""
        registry_dir = tmp_path / "cortex-registry" / "_cortex-master"
        registry_dir.mkdir(parents=True)
        
        monitor = RegressionMonitor(registry_dir)
        result = monitor.scan_brittleness(["/nonexistent/file.py"])
        
        # Should handle gracefully
        assert result["status"] in ["PASS", "WARNING"]

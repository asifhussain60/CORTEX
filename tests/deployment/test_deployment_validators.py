"""
Tests for Deployment Validators (Phase 3)

Tests:
- PackagePurityChecker: Admin leak detection
- DeploymentGates: Quality gate enforcement
- BinarySizeMonitor: Package size tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.deployment.package_purity_checker import PackagePurityChecker
from src.deployment.deployment_gates import DeploymentGates
from src.deployment.binary_size_monitor import BinarySizeMonitor


# ===== PackagePurityChecker Tests =====

def test_package_purity_checker_initialization():
    """Test PackagePurityChecker initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        checker = PackagePurityChecker(Path(tmpdir), Path(tmpdir))
        assert checker.project_root == Path(tmpdir)


def test_check_admin_directories_clean():
    """Test admin directory check with clean package."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        package_root = project_root / "dist"
        
        # Create clean package structure
        (package_root / "src" / "core").mkdir(parents=True)
        (package_root / "src" / "core" / "main.py").write_text("# Core code")
        
        checker = PackagePurityChecker(package_root, project_root)
        violations = checker._check_admin_directories()
        
        assert len(violations) == 0


def test_check_admin_directories_violation():
    """Test admin directory check with admin leak."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        package_root = project_root / "dist"
        
        # Create package with admin code
        admin_dir = package_root / "src" / "operations" / "modules" / "admin"
        admin_dir.mkdir(parents=True)
        (admin_dir / "system_alignment_orchestrator.py").write_text("# Admin code")
        
        checker = PackagePurityChecker(package_root, project_root)
        violations = checker._check_admin_directories()
        
        assert len(violations) > 0
        assert any("admin" in v.lower() for v in violations)


def test_check_prompt_sanitization_clean():
    """Test prompt sanitization with clean response templates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        package_root = project_root / "dist"
        
        # Create prompt without admin commands
        prompt_file = package_root / ".github" / "prompts" / "CORTEX.prompt.md"
        prompt_file.parent.mkdir(parents=True)
        prompt_file.write_text("# CORTEX\n\nHelp: Show available commands")
        
        checker = PackagePurityChecker(package_root, project_root)
        violations = checker._check_prompt_sanitization()
        
        assert len(violations) == 0


def test_check_prompt_sanitization_violation():
    """Test prompt sanitization with admin commands."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        package_root = project_root / "dist"
        
        # Create prompt with admin commands
        prompt_file = package_root / ".github" / "prompts" / "CORTEX.prompt.md"
        prompt_file.parent.mkdir(parents=True)
        prompt_file.write_text("# CORTEX\n\nalign - Run system alignment validation")
        
        checker = PackagePurityChecker(package_root, project_root)
        violations = checker._check_prompt_sanitization()
        
        assert len(violations) > 0
        assert any("align" in v.lower() for v in violations)


def test_validate_purity_full_check():
    """Test full purity validation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        package_root = project_root / "dist"
        
        # Create minimal clean structure
        (package_root / "src" / "core").mkdir(parents=True)
        (package_root / "src" / "core" / "main.py").write_text("# Core code")
        
        checker = PackagePurityChecker(package_root, project_root)
        result = checker.validate_purity()
        
        assert result["is_pure"]
        assert len(result["admin_leaks"]) == 0


# ===== DeploymentGates Tests =====

@pytest.fixture
def mock_validators():
    """Create mock validators for deployment gates."""
    mock_integration_scorer = MagicMock()
    mock_test_validator = MagicMock()
    mock_doc_validator = MagicMock()
    
    return {
        "integration_scorer": mock_integration_scorer,
        "test_validator": mock_test_validator,
        "doc_validator": mock_doc_validator
    }


def test_deployment_gates_initialization():
    """Test DeploymentGates initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gates = DeploymentGates(Path(tmpdir))
        assert gates.project_root == Path(tmpdir)


def test_check_integration_scores_pass(mock_validators):
    """Test integration score gate with passing scores."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gates = DeploymentGates(Path(tmpdir))
        
        # Mock alignment report with high scores
        alignment_report = {
            "orchestrators": [
                {
                    "name": "TestOrchestrator",
                    "is_admin": False,
                    "integration_score": 85
                }
            ]
        }
        
        result = gates._validate_integration_scores(alignment_report)
        
        assert result["passed"]


def test_check_integration_scores_fail(mock_validators):
    """Test integration score gate with failing scores."""
    with tempfile.TemporaryDirectory() as tmpdir:
        gates = DeploymentGates(Path(tmpdir))
        
        # Mock alignment report with low scores
        alignment_report = {
            "feature_scores": {
                "TestOrchestrator": {
                    "score": 60,
                    "issues": ["Low integration"]
                }
            }
        }
        
        result = gates._validate_integration_scores(alignment_report)
        
        assert not result["passed"]
        assert "below" in result["message"].lower() or "threshold" in result["message"].lower()


def test_check_no_mocks_clean():
    """Test no-mocks gate with clean code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create clean source file
        src_dir = project_root / "src"
        src_dir.mkdir(parents=True)
        (src_dir / "main.py").write_text("import logging\nlogger = logging.getLogger(__name__)")
        
        gates = DeploymentGates(project_root)
        result = gates._validate_no_mocks()
        
        assert result["passed"]


def test_check_no_mocks_violation():
    """Test no-mocks gate with mocks in production code."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create source file with mocks
        src_dir = project_root / "src"
        src_dir.mkdir(parents=True)
        (src_dir / "main.py").write_text("from unittest.mock import Mock\nmock_obj = Mock()")
        
        gates = DeploymentGates(project_root)
        result = gates._validate_no_mocks()
        
        assert not result["passed"]
        assert "mock" in result["message"].lower()


def test_check_version_consistency_pass():
    """Test version consistency gate with matching versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create version files with matching versions
        (project_root / "VERSION").write_text("3.2.0")
        (project_root / "package.json").write_text('{"version": "3.2.0"}')
        
        prompt_dir = project_root / ".github" / "prompts"
        prompt_dir.mkdir(parents=True)
        (prompt_dir / "CORTEX.prompt.md").write_text("Version: 3.2.0")
        
        gates = DeploymentGates(project_root)
        result = gates._validate_version_consistency()
        
        assert result["passed"]


def test_check_version_consistency_fail():
    """Test version consistency gate with mismatched versions."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create version files with mismatched versions
        (project_root / "VERSION").write_text("3.2.0")
        (project_root / "package.json").write_text('{"version": "3.1.0"}')
        
        gates = DeploymentGates(project_root)
        result = gates._validate_version_consistency()
        
        assert not result["passed"]
        assert "version" in result["message"].lower()


# ===== BinarySizeMonitor Tests =====

def test_binary_size_monitor_initialization():
    """Test BinarySizeMonitor initialization."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = BinarySizeMonitor(Path(tmpdir))
        assert monitor.project_root == Path(tmpdir)


def test_measure_package_size():
    """Test package size measurement."""
    with tempfile.TemporaryDirectory() as tmpdir:
        package_root = Path(tmpdir)
        
        # Create test files
        (package_root / "file1.py").write_text("# " * 100)
        (package_root / "file2.txt").write_text("test " * 50)
        sub_dir = package_root / "subdir"
        sub_dir.mkdir()
        (sub_dir / "file3.json").write_text('{"key": "value"}')
        
        monitor = BinarySizeMonitor(package_root)
        measurement = monitor.measure_package_size(package_root)
        
        assert measurement["total_files"] == 3
        assert measurement["total_size_bytes"] > 0
        assert ".py" in measurement["size_by_extension"]
        assert "subdir" in measurement["size_by_directory"]
        assert len(measurement["largest_files"]) > 0


def test_measure_package_size_nonexistent():
    """Test package size measurement with nonexistent path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = BinarySizeMonitor(Path(tmpdir))
        measurement = monitor.measure_package_size(Path(tmpdir) / "nonexistent")
        
        assert "error" in measurement


def test_compare_with_history_no_history():
    """Test size comparison with no history."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = BinarySizeMonitor(Path(tmpdir))
        
        current = {"total_size_bytes": 1000}
        comparison = monitor.compare_with_history(current)
        
        assert not comparison["has_history"]
        assert comparison["size_change_percent"] == 0.0


def test_compare_with_history_growth():
    """Test size comparison with growth."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = BinarySizeMonitor(Path(tmpdir))
        
        # Create fake history
        history = [{"total_size_bytes": 1000}]
        monitor.history_file.parent.mkdir(parents=True, exist_ok=True)
        with open(monitor.history_file, "w") as f:
            json.dump(history, f)
        
        # Compare with larger size
        current = {"total_size_bytes": 1200}
        comparison = monitor.compare_with_history(current)
        
        assert comparison["has_history"]
        assert comparison["size_change_percent"] == 20.0
        assert comparison["alert_threshold_exceeded"]  # >10% threshold


def test_save_measurement():
    """Test saving size measurement."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = BinarySizeMonitor(Path(tmpdir))
        
        measurement = {
            "timestamp": "2025-01-01T00:00:00",
            "total_size_bytes": 5000,
            "total_files": 10
        }
        
        monitor.save_measurement(measurement)
        
        assert monitor.history_file.exists()
        
        with open(monitor.history_file, "r") as f:
            history = json.load(f)
        
        assert len(history) == 1
        assert history[0]["total_size_bytes"] == 5000


def test_get_size_trend():
    """Test retrieving size trend."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monitor = BinarySizeMonitor(Path(tmpdir))
        
        # Save multiple measurements
        for i in range(5):
            measurement = {
                "timestamp": f"2025-01-0{i+1}T00:00:00",
                "total_size_bytes": 1000 * (i + 1)
            }
            monitor.save_measurement(measurement)
        
        trend = monitor.get_size_trend(limit=3)
        
        assert len(trend) == 3
        # Should be most recent first
        assert trend[0]["total_size_bytes"] == 5000


def test_format_bytes():
    """Test byte formatting."""
    assert "1.0 KB" in BinarySizeMonitor._format_bytes(1024)
    assert "1.0 MB" in BinarySizeMonitor._format_bytes(1024 * 1024)
    assert "500.0 B" in BinarySizeMonitor._format_bytes(500)

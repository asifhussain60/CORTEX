"""
Tests for DependencyDriftDetector - P0-027 AUDIT check.

AC_START: AC-ENH053-001
Description: TDD for dependency drift detection system
Author: Asif Hussain
Date: 2026-02-07
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from cortex.orchestrators.audit.dependency_drift_detector import (
    DependencyDriftDetector,
    DependencyDriftResult,
    Package,
)


class TestDependencyDriftDetector:
    """Test dependency drift detection between requirements.txt and installed packages."""

    @pytest.fixture
    def detector(self):
        """Create DependencyDriftDetector instance."""
        return DependencyDriftDetector()

    @pytest.fixture
    def sample_repo_path(self, tmp_path):
        """Create sample repository with requirements.txt."""
        repo_path = tmp_path / "sample_repo"
        repo_path.mkdir()
        requirements = repo_path / "requirements.txt"
        requirements.write_text(
            "flask==2.3.0\n"
            "requests>=2.28.0\n"
            "pytest==7.4.0\n"
            "# Comment line\n"
            "numpy>=1.24.0\n"
        )
        return repo_path

    def test_detector_initialization(self, detector):
        """Test detector initializes correctly."""
        assert detector is not None
        assert hasattr(detector, "analyze")

    def test_parse_requirements_txt(self, detector, sample_repo_path):
        """Test parsing requirements.txt file."""
        packages = detector._parse_requirements_txt(sample_repo_path)
        
        assert len(packages) == 4
        assert Package("flask", "2.3.0") in packages
        assert Package("requests", "2.28.0") in packages
        assert Package("pytest", "7.4.0") in packages
        assert Package("numpy", "1.24.0") in packages

    def test_parse_requirements_txt_missing_file(self, detector, tmp_path):
        """Test parsing when requirements.txt doesn't exist."""
        packages = detector._parse_requirements_txt(tmp_path)
        assert packages == set()

    @patch("subprocess.run")
    def test_get_installed_packages(self, mock_run, detector):
        """Test getting installed packages via pip freeze."""
        mock_run.return_value = Mock(
            stdout="flask==2.3.0\nrequests==2.28.1\nnumpy==1.24.2\nscikit-learn==1.3.0\n",
            returncode=0,
        )
        
        packages = detector._get_installed_packages()
        
        assert len(packages) == 4
        assert Package("flask", "2.3.0") in packages
        assert Package("requests", "2.28.1") in packages
        assert Package("numpy", "1.24.2") in packages
        assert Package("scikit-learn", "1.3.0") in packages

    @patch("subprocess.run")
    def test_get_installed_packages_failure(self, mock_run, detector):
        """Test handling pip freeze failure."""
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Error")
        
        packages = detector._get_installed_packages()
        assert packages == set()

    def test_detect_missing_packages(self, detector):
        """Test detecting missing packages."""
        required = {Package("flask", "2.3.0"), Package("pytest", "7.4.0")}
        installed = {Package("flask", "2.3.0")}
        
        missing = detector._detect_missing(required, installed)
        
        assert len(missing) == 1
        assert Package("pytest", "7.4.0") in missing

    def test_detect_extra_packages(self, detector):
        """Test detecting extra packages."""
        required = {Package("flask", "2.3.0")}
        installed = {Package("flask", "2.3.0"), Package("pytest", "7.4.0")}
        
        extra = detector._detect_extra(required, installed)
        
        assert len(extra) == 1
        assert Package("pytest", "7.4.0") in extra

    def test_detect_version_mismatches(self, detector):
        """Test detecting version mismatches."""
        required = {Package("flask", "2.3.0"), Package("requests", "2.28.0")}
        installed = {Package("flask", "2.3.1"), Package("requests", "2.28.0")}
        
        mismatched = detector._detect_mismatches(required, installed)
        
        assert len(mismatched) == 1
        assert ("flask", "2.3.0", "2.3.1") in mismatched

    @patch("subprocess.run")
    def test_analyze_no_drift(self, mock_run, detector, sample_repo_path):
        """Test analysis when no drift detected."""
        mock_run.return_value = Mock(
            stdout="flask==2.3.0\nrequests==2.28.0\npytest==7.4.0\nnumpy==1.24.0\n",
            returncode=0,
        )
        
        result = detector.analyze(sample_repo_path)
        
        assert result.missing == set()
        assert result.extra == set()
        assert result.mismatched == set()
        assert result.severity == "P2"
        assert result.has_drift is False

    @patch("subprocess.run")
    def test_analyze_with_drift(self, mock_run, detector, sample_repo_path):
        """Test analysis with drift detected."""
        mock_run.return_value = Mock(
            stdout="flask==2.3.0\nrequests==2.28.1\nscikit-learn==1.3.0\n",
            returncode=0,
        )
        
        result = detector.analyze(sample_repo_path)
        
        assert len(result.missing) == 2  # pytest, numpy
        assert len(result.extra) == 1  # scikit-learn
        assert len(result.mismatched) == 1  # requests version
        assert result.severity == "P0"  # Missing packages = P0
        assert result.has_drift is True

    def test_generate_fix_commands(self, detector):
        """Test generating pip install commands for fixes."""
        result = DependencyDriftResult(
            missing={Package("pytest", "7.4.0"), Package("numpy", "1.24.0")},
            extra={Package("scikit-learn", "1.3.0")},
            mismatched={("requests", "2.28.0", "2.28.1")},
            severity="P0",
        )
        
        commands = detector.generate_fix_commands(result)
        
        # Check install command contains both packages (order may vary)
        install_cmd = [cmd for cmd in commands if cmd.startswith("pip install") and "pytest" in cmd]
        assert len(install_cmd) == 1
        assert "pytest==7.4.0" in install_cmd[0]
        assert "numpy==1.24.0" in install_cmd[0]
        
        # Check uninstall command
        assert "pip uninstall scikit-learn" in commands
        
        # Check version fix command
        assert "pip install requests==2.28.0" in commands


class TestDependencyDriftResult:
    """Test DependencyDriftResult model."""

    def test_result_initialization(self):
        """Test result model initialization."""
        result = DependencyDriftResult(
            missing={Package("flask", "2.3.0")},
            extra={Package("pytest", "7.4.0")},
            mismatched={("requests", "2.28.0", "2.28.1")},
            severity="P0",
        )
        
        assert len(result.missing) == 1
        assert len(result.extra) == 1
        assert len(result.mismatched) == 1
        assert result.severity == "P0"

    def test_has_drift_property(self):
        """Test has_drift property calculation."""
        result_no_drift = DependencyDriftResult(
            missing=set(), extra=set(), mismatched=set(), severity="P2"
        )
        assert result_no_drift.has_drift is False
        
        result_with_drift = DependencyDriftResult(
            missing={Package("flask", "2.3.0")}, extra=set(), mismatched=set(), severity="P0"
        )
        assert result_with_drift.has_drift is True

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = DependencyDriftResult(
            missing={Package("flask", "2.3.0")},
            extra=set(),
            mismatched=set(),
            severity="P0",
        )
        
        data = result.to_dict()
        
        assert data["severity"] == "P0"
        assert data["has_drift"] is True
        assert len(data["missing"]) == 1
        assert data["missing"][0]["name"] == "flask"


# AC_COMPLETE: AC-ENH053-001 ✅ 12/12 tests defined (RED phase)

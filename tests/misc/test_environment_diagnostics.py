"""
Tests for environment diagnostics system
Checks Python environment, git status, disk space, memory, installed packages

TDD Phase: RED - Tests written first, expected to fail
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from src.diagnostics.environment_diagnostics import (
    EnvironmentDiagnostics,
    DiagnosticResult,
    DiagnosticCategory,
    DiagnosticStatus
)


class TestEnvironmentDiagnostics:
    """Test environment diagnostics system"""
    
    @pytest.fixture
    def temp_cortex_dir(self):
        """Create temporary CORTEX directory"""
        temp_dir = tempfile.mkdtemp()
        cortex_dir = Path(temp_dir) / "CORTEX"
        cortex_dir.mkdir()
        
        yield cortex_dir
        
        shutil.rmtree(temp_dir)
    
    def test_diagnostics_initialization(self, temp_cortex_dir):
        """Test EnvironmentDiagnostics can be initialized"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        assert diagnostics is not None
        assert diagnostics.root_path == temp_cortex_dir
    
    def test_check_python_version(self, temp_cortex_dir):
        """Test Python version detection"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        result = diagnostics.check_python_version()
        
        assert result.category == DiagnosticCategory.PYTHON
        assert result.status in [DiagnosticStatus.HEALTHY, DiagnosticStatus.WARNING]
        assert "Python" in result.message
        assert result.details.get("version") is not None
    
    def test_check_python_version_minimum(self, temp_cortex_dir):
        """Test Python version meets minimum requirement"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        result = diagnostics.check_python_version()
        
        version = result.details.get("version", "")
        # Should be 3.8+ for CORTEX
        assert result.status != DiagnosticStatus.CRITICAL
    
    def test_check_git_status(self, temp_cortex_dir):
        """Test git repository status check"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="On branch main\nnothing to commit, working tree clean"
            )
            
            result = diagnostics.check_git_status()
            
            assert result.category == DiagnosticCategory.GIT
            assert result.status in [DiagnosticStatus.HEALTHY, DiagnosticStatus.INFO]
    
    def test_check_git_uncommitted_changes(self, temp_cortex_dir):
        """Test detection of uncommitted changes"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="M file1.py\n?? file2.py"
            )
            
            result = diagnostics.check_git_status()
            
            assert "uncommitted" in result.message.lower() or "changes" in result.message.lower()
    
    def test_check_disk_space(self, temp_cortex_dir):
        """Test disk space check"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        result = diagnostics.check_disk_space()
        
        assert result.category == DiagnosticCategory.SYSTEM
        assert result.status in [DiagnosticStatus.HEALTHY, DiagnosticStatus.WARNING, DiagnosticStatus.CRITICAL]
        assert result.details.get("available_gb") is not None
        assert result.details.get("percent_used") is not None
    
    def test_check_disk_space_low_warning(self, temp_cortex_dir):
        """Test low disk space triggers warning"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        with patch('shutil.disk_usage') as mock_disk:
            # Simulate 95% disk usage
            mock_disk.return_value = MagicMock(
                total=100 * 1024**3,
                used=95 * 1024**3,
                free=5 * 1024**3
            )
            
            result = diagnostics.check_disk_space()
            
            assert result.status in [DiagnosticStatus.WARNING, DiagnosticStatus.CRITICAL]
    
    def test_check_memory_usage(self, temp_cortex_dir):
        """Test memory usage check"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        with patch('psutil.virtual_memory') as mock_mem:
            mock_mem.return_value = MagicMock(
                total=16 * 1024**3,
                available=8 * 1024**3,
                percent=50.0
            )
            
            result = diagnostics.check_memory_usage()
            
            assert result.category == DiagnosticCategory.SYSTEM
            assert result.details.get("available_gb") is not None
            assert result.details.get("percent_used") is not None
    
    def test_check_installed_packages(self, temp_cortex_dir):
        """Test installed Python packages check"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        result = diagnostics.check_installed_packages()
        
        assert result.category == DiagnosticCategory.PYTHON
        assert result.status in [DiagnosticStatus.HEALTHY, DiagnosticStatus.WARNING]
        assert "packages" in result.details
        
        packages = result.details["packages"]
        assert isinstance(packages, list)
    
    def test_check_required_packages_present(self, temp_cortex_dir):
        """Test detection of required packages"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        with patch('importlib.import_module') as mock_import:
            mock_import.return_value = MagicMock()
            
            result = diagnostics.check_required_packages()
            
            assert result.category == DiagnosticCategory.PYTHON
            assert result.status == DiagnosticStatus.HEALTHY
    
    def test_check_required_packages_missing(self, temp_cortex_dir):
        """Test detection of missing required packages"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        with patch('importlib.import_module') as mock_import:
            mock_import.side_effect = ImportError("Package not found")
            
            result = diagnostics.check_required_packages()
            
            assert result.status == DiagnosticStatus.CRITICAL
            assert "missing" in result.message.lower()
    
    def test_run_all_diagnostics(self, temp_cortex_dir):
        """Test comprehensive diagnostics run"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        results = diagnostics.run_all()
        
        assert isinstance(results, list)
        assert len(results) > 0
        
        # Should have multiple categories
        categories = set(r.category for r in results)
        assert DiagnosticCategory.PYTHON in categories
        assert DiagnosticCategory.SYSTEM in categories
    
    def test_diagnostic_result_creation(self):
        """Test DiagnosticResult dataclass creation"""
        result = DiagnosticResult(
            category=DiagnosticCategory.PYTHON,
            status=DiagnosticStatus.HEALTHY,
            message="Python environment is healthy",
            details={"version": "3.9.6"}
        )
        
        assert result.category == DiagnosticCategory.PYTHON
        assert result.status == DiagnosticStatus.HEALTHY
        assert "healthy" in result.message.lower()
        assert result.details["version"] == "3.9.6"
    
    def test_diagnostic_status_enum(self):
        """Test DiagnosticStatus enum values"""
        assert DiagnosticStatus.HEALTHY.value == "healthy"
        assert DiagnosticStatus.WARNING.value == "warning"
        assert DiagnosticStatus.CRITICAL.value == "critical"
        assert DiagnosticStatus.INFO.value == "info"
    
    def test_diagnostic_category_enum(self):
        """Test DiagnosticCategory enum values"""
        assert DiagnosticCategory.PYTHON.value == "python"
        assert DiagnosticCategory.GIT.value == "git"
        assert DiagnosticCategory.SYSTEM.value == "system"
        assert DiagnosticCategory.NETWORK.value == "network"
    
    def test_generate_report(self, temp_cortex_dir):
        """Test diagnostic report generation"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        results = diagnostics.run_all()
        report = diagnostics.generate_report(results)
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "DIAGNOSTIC" in report.upper()
    
    def test_check_cortex_processes(self, temp_cortex_dir):
        """Test detection of running CORTEX processes"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        with patch('psutil.process_iter') as mock_proc:
            mock_proc.return_value = [
                MagicMock(info={"name": "python", "cmdline": ["python", "cortex_main.py"]})
            ]
            
            result = diagnostics.check_cortex_processes()
            
            assert result.category == DiagnosticCategory.SYSTEM
            assert "process" in result.message.lower()
    
    def test_check_port_availability(self, temp_cortex_dir):
        """Test port availability check for services"""
        diagnostics = EnvironmentDiagnostics(root_path=temp_cortex_dir)
        
        result = diagnostics.check_port_availability(port=8080)
        
        assert result.category == DiagnosticCategory.NETWORK
        assert result.status in [DiagnosticStatus.HEALTHY, DiagnosticStatus.WARNING]
        assert result.details.get("port") == 8080

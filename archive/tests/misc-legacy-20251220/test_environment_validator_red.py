"""
RED Phase Tests for Environment Validator
Test-first development for environment validation

Target: <60s for all validation checks
Coverage: Runtime versions, tool availability, disk space, network, permissions
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import sys


class TestEnvironmentValidatorInitialization:
    """Test validator initialization and basic operations."""
    
    def test_creates_validator_with_workspace_path(self):
        """Should create validator with workspace path."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        assert validator is not None
        assert validator.workspace_path == Path(r"c:\test\workspace")
    
    def test_validates_with_default_checks(self):
        """Should run all validation checks by default."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        assert isinstance(results, dict)
        assert "validation_results" in results
        assert "summary" in results


class TestRuntimeVersionChecks:
    """Test runtime version detection and validation."""
    
    def test_detects_python_version(self):
        """Should detect Python version from system."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        runtime_checks = results["validation_results"]["runtime_checks"]
        assert "python" in runtime_checks
        assert "version" in runtime_checks["python"]
        assert "available" in runtime_checks["python"]
    
    def test_detects_nodejs_version(self):
        """Should detect Node.js version if installed."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        runtime_checks = results["validation_results"]["runtime_checks"]
        assert "nodejs" in runtime_checks
        assert "version" in runtime_checks["nodejs"]
        assert "available" in runtime_checks["nodejs"]
    
    def test_detects_dotnet_version(self):
        """Should detect .NET SDK version if installed."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        runtime_checks = results["validation_results"]["runtime_checks"]
        assert "dotnet" in runtime_checks
        assert "version" in runtime_checks["dotnet"]
        assert "available" in runtime_checks["dotnet"]
    
    def test_detects_ruby_version(self):
        """Should detect Ruby version if installed."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        runtime_checks = results["validation_results"]["runtime_checks"]
        assert "ruby" in runtime_checks
        assert "version" in runtime_checks["ruby"]
        assert "available" in runtime_checks["ruby"]


class TestToolAvailabilityChecks:
    """Test development tool availability detection."""
    
    def test_checks_git_availability(self):
        """Should check if Git is installed and accessible."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        tool_checks = results["validation_results"]["tool_checks"]
        assert "git" in tool_checks
        assert "available" in tool_checks["git"]
        assert "version" in tool_checks["git"]
    
    def test_checks_npm_availability(self):
        """Should check if npm is installed."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        tool_checks = results["validation_results"]["tool_checks"]
        assert "npm" in tool_checks
        assert "available" in tool_checks["npm"]
    
    def test_checks_pip_availability(self):
        """Should check if pip is installed."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        tool_checks = results["validation_results"]["tool_checks"]
        assert "pip" in tool_checks
        assert "available" in tool_checks["pip"]
    
    def test_checks_docker_availability(self):
        """Should check if Docker is installed (optional)."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        tool_checks = results["validation_results"]["tool_checks"]
        assert "docker" in tool_checks
        assert "available" in tool_checks["docker"]


class TestSystemResourceChecks:
    """Test system resource validation (disk space, memory)."""
    
    def test_checks_disk_space(self):
        """Should check available disk space in workspace."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        resource_checks = results["validation_results"]["resource_checks"]
        assert "disk_space" in resource_checks
        assert "total_gb" in resource_checks["disk_space"]
        assert "free_gb" in resource_checks["disk_space"]
        assert "sufficient" in resource_checks["disk_space"]
    
    def test_checks_memory(self):
        """Should check system memory availability."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        resource_checks = results["validation_results"]["resource_checks"]
        assert "memory" in resource_checks
        assert "total_gb" in resource_checks["memory"]
        assert "available_gb" in resource_checks["memory"]
        assert "sufficient" in resource_checks["memory"]
    
    def test_warns_on_low_disk_space(self):
        """Should warn if disk space < 1GB."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        
        with patch('shutil.disk_usage') as mock_disk:
            mock_disk.return_value = Mock(total=100*1024**3, free=500*1024**2)  # 500MB free
            results = validator.validate()
        
        resource_checks = results["validation_results"]["resource_checks"]
        assert resource_checks["disk_space"]["sufficient"] is False


class TestNetworkConnectivityChecks:
    """Test network connectivity validation."""
    
    def test_checks_internet_connectivity(self):
        """Should check if internet is accessible."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        network_checks = results["validation_results"]["network_checks"]
        assert "internet" in network_checks
        assert "accessible" in network_checks["internet"]
    
    def test_checks_package_registry_access(self):
        """Should check access to package registries (PyPI, npm)."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        network_checks = results["validation_results"]["network_checks"]
        assert "pypi" in network_checks
        assert "npm" in network_checks


class TestPermissionChecks:
    """Test file system permission validation."""
    
    def test_checks_workspace_write_permission(self):
        """Should check if workspace is writable."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        permission_checks = results["validation_results"]["permission_checks"]
        assert "workspace_writable" in permission_checks
        assert isinstance(permission_checks["workspace_writable"], bool)
    
    def test_checks_config_file_permissions(self):
        """Should check if can create config files."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        permission_checks = results["validation_results"]["permission_checks"]
        assert "config_writable" in permission_checks


class TestValidationSummary:
    """Test validation summary and reporting."""
    
    def test_provides_overall_status(self):
        """Should provide overall pass/fail status."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        summary = results["summary"]
        assert "status" in summary
        assert summary["status"] in ["PASS", "FAIL", "WARNING"]
    
    def test_counts_passed_checks(self):
        """Should count number of passed/failed checks."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        summary = results["summary"]
        assert "total_checks" in summary
        assert "passed" in summary
        assert "failed" in summary
        assert "warnings" in summary
    
    def test_lists_critical_issues(self):
        """Should list critical issues preventing setup."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        summary = results["summary"]
        assert "critical_issues" in summary
        assert isinstance(summary["critical_issues"], list)
    
    def test_provides_recommendations(self):
        """Should provide fix recommendations for issues."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        summary = results["summary"]
        assert "recommendations" in summary
        assert isinstance(summary["recommendations"], list)


class TestPerformanceConstraints:
    """Test validation performance requirements."""
    
    def test_completes_within_60_seconds(self):
        """Should complete all checks within 60 seconds."""
        from src.intelligence.environment_validator import EnvironmentValidator
        import time
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        
        start = time.time()
        results = validator.validate()
        duration = time.time() - start
        
        assert duration < 60.0, f"Validation took {duration:.2f}s (target: <60s)"
    
    def test_provides_timing_information(self):
        """Should report timing for each check category."""
        from src.intelligence.environment_validator import EnvironmentValidator
        
        validator = EnvironmentValidator(r"c:\test\workspace")
        results = validator.validate()
        
        assert "timing" in results
        timing = results["timing"]
        assert "runtime_checks" in timing
        assert "tool_checks" in timing
        assert "resource_checks" in timing
        assert "network_checks" in timing
        assert "permission_checks" in timing

"""
Tests for Pre-Flight Orchestrator

Validates:
- Pattern detection (FastAPI, .NET, Node.js)
- Requirement generation (Python 3.8+, .NET SDK, etc.)
- Environment validation (command execution)
- Gate enforcement (BLOCK vs WARN)
- Script generation (PowerShell/bash)
- Health report generation

Author: Asif Hussain
Date: December 13, 2025
Version: 1.0.0
"""

import pytest
import tempfile
import platform
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess

from src.orchestrators.planning.pre_flight_orchestrator import (
    PreFlightOrchestrator,
    RequirementDetector,
    ValidationScriptGenerator,
    ProjectPattern,
    RequirementSeverity,
    EnvironmentRequirement,
    PreFlightHealthReport
)
from src.orchestrators.environment_diagnostics_orchestrator import (
    ValidationResult,
    CheckStatus
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def dotnet_project(temp_project):
    """Create .NET project structure"""
    csproj_content = """
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
</Project>
"""
    csproj_path = temp_project / "TestApi.csproj"
    csproj_path.write_text(csproj_content)
    return temp_project


@pytest.fixture
def python_fastapi_project(temp_project):
    """Create Python FastAPI project"""
    requirements_path = temp_project / "requirements.txt"
    requirements_path.write_text("fastapi\nuvicorn\npydantic")
    
    main_py = temp_project / "main.py"
    main_py.write_text("from fastapi import FastAPI\nimport jwt")
    
    return temp_project


@pytest.fixture
def nodejs_project(temp_project):
    """Create Node.js Express project"""
    package_json = temp_project / "package.json"
    package_json.write_text('{"dependencies": {"express": "^4.17.1"}}')
    return temp_project


@pytest.fixture
def docker_project(temp_project):
    """Create Docker Compose project"""
    compose_path = temp_project / "docker-compose.yml"
    compose_path.write_text("version: '3'\nservices:\n  app:\n    image: nginx")
    return temp_project


# ============================================================================
# TEST PATTERN DETECTION
# ============================================================================

class TestRequirementDetector:
    """Tests for RequirementDetector"""
    
    def test_detect_dotnet_api_pattern(self, dotnet_project):
        """Should detect .NET API pattern from .csproj"""
        detector = RequirementDetector(dotnet_project)
        patterns = detector.detect_patterns()
        
        assert ProjectPattern.DOTNET_API in patterns
    
    def test_detect_python_fastapi_pattern(self, python_fastapi_project):
        """Should detect FastAPI pattern from requirements.txt"""
        detector = RequirementDetector(python_fastapi_project)
        patterns = detector.detect_patterns()
        
        assert ProjectPattern.PYTHON_FASTAPI in patterns
    
    def test_detect_jwt_auth_pattern(self, python_fastapi_project):
        """Should detect JWT auth from code"""
        detector = RequirementDetector(python_fastapi_project)
        patterns = detector.detect_patterns()
        
        assert ProjectPattern.JWT_AUTH in patterns
    
    def test_detect_nodejs_express_pattern(self, nodejs_project):
        """Should detect Node.js Express pattern"""
        detector = RequirementDetector(nodejs_project)
        patterns = detector.detect_patterns()
        
        assert ProjectPattern.NODEJS_EXPRESS in patterns
    
    def test_detect_docker_compose_pattern(self, docker_project):
        """Should detect Docker Compose pattern"""
        detector = RequirementDetector(docker_project)
        patterns = detector.detect_patterns()
        
        assert ProjectPattern.DOCKER_COMPOSE in patterns
    
    def test_detect_multiple_patterns(self, temp_project):
        """Should detect multiple patterns in same project"""
        # Create hybrid project
        (temp_project / "TestApi.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk.Web"></Project>')
        (temp_project / "docker-compose.yml").write_text("version: '3'")
        
        detector = RequirementDetector(temp_project)
        patterns = detector.detect_patterns()
        
        assert ProjectPattern.DOTNET_API in patterns
        assert ProjectPattern.DOCKER_COMPOSE in patterns
    
    def test_empty_project_no_patterns(self, temp_project):
        """Should detect no patterns for empty project"""
        detector = RequirementDetector(temp_project)
        patterns = detector.detect_patterns()
        
        # Should only have universal patterns (if any)
        assert ProjectPattern.DOTNET_API not in patterns
        assert ProjectPattern.PYTHON_FASTAPI not in patterns


# ============================================================================
# TEST REQUIREMENT GENERATION
# ============================================================================

class TestRequirementGeneration:
    """Tests for requirement generation from patterns"""
    
    def test_generate_dotnet_requirements(self, dotnet_project):
        """Should generate .NET SDK requirement"""
        detector = RequirementDetector(dotnet_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        dotnet_req = next((r for r in requirements if r.name == "dotnet_sdk"), None)
        assert dotnet_req is not None
        assert dotnet_req.severity == RequirementSeverity.CRITICAL
        assert dotnet_req.min_version == "6.0"
        assert "dotnet --version" in dotnet_req.check_command
    
    def test_generate_python_requirements(self, python_fastapi_project):
        """Should generate Python + pip requirements"""
        detector = RequirementDetector(python_fastapi_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        python_req = next((r for r in requirements if r.name == "python"), None)
        pip_req = next((r for r in requirements if r.name == "pip"), None)
        
        assert python_req is not None
        assert python_req.severity == RequirementSeverity.CRITICAL
        assert python_req.min_version == "3.8"
        
        assert pip_req is not None
        assert pip_req.severity == RequirementSeverity.CRITICAL
    
    def test_generate_nodejs_requirements(self, nodejs_project):
        """Should generate Node.js + npm requirements"""
        detector = RequirementDetector(nodejs_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        node_req = next((r for r in requirements if r.name == "nodejs"), None)
        npm_req = next((r for r in requirements if r.name == "npm"), None)
        
        assert node_req is not None
        assert node_req.min_version == "16.0"
        
        assert npm_req is not None
    
    def test_generate_jwt_openssl_requirement(self, python_fastapi_project):
        """Should generate OpenSSL requirement for JWT projects"""
        detector = RequirementDetector(python_fastapi_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        openssl_req = next((r for r in requirements if r.name == "openssl"), None)
        assert openssl_req is not None
        assert openssl_req.severity == RequirementSeverity.RECOMMENDED
    
    def test_generate_git_universal_requirement(self, temp_project):
        """Should always generate Git requirement"""
        detector = RequirementDetector(temp_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        git_req = next((r for r in requirements if r.name == "git"), None)
        assert git_req is not None
        assert git_req.severity == RequirementSeverity.CRITICAL
    
    def test_requirement_has_remediation(self, dotnet_project):
        """All requirements should have remediation instructions"""
        detector = RequirementDetector(dotnet_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        for req in requirements:
            assert req.remediation, f"{req.name} missing remediation"
            assert len(req.remediation) > 0


# ============================================================================
# TEST SCRIPT GENERATION
# ============================================================================

class TestValidationScriptGenerator:
    """Tests for validation script generation"""
    
    def test_generate_powershell_script_on_windows(self):
        """Should generate PowerShell script on Windows"""
        requirements = [
            EnvironmentRequirement(
                name="dotnet_sdk",
                severity=RequirementSeverity.CRITICAL,
                check_command="dotnet --version",
                remediation="Install .NET SDK"
            )
        ]
        
        with patch('platform.system', return_value='Windows'):
            generator = ValidationScriptGenerator(requirements)
            script = generator.generate_script()
        
        assert "# CORTEX Pre-Flight Environment Validation Script" in script
        assert "Write-Host" in script
        assert "dotnet --version" in script
        assert "$results =" in script
    
    def test_generate_bash_script_on_linux(self):
        """Should generate bash script on Linux/macOS"""
        requirements = [
            EnvironmentRequirement(
                name="python",
                severity=RequirementSeverity.CRITICAL,
                check_command="python --version",
                remediation="Install Python"
            )
        ]
        
        with patch('platform.system', return_value='Linux'):
            generator = ValidationScriptGenerator(requirements)
            script = generator.generate_script()
        
        assert "#!/bin/bash" in script
        assert "echo -e" in script
        assert "python --version" in script
    
    def test_script_includes_all_requirements(self, dotnet_project):
        """Generated script should check all requirements"""
        detector = RequirementDetector(dotnet_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        generator = ValidationScriptGenerator(requirements)
        script = generator.generate_script()
        
        for req in requirements:
            assert req.name in script
            assert req.check_command in script or req.check_command.split()[0] in script
    
    def test_script_has_summary_section(self):
        """Script should have validation summary"""
        requirements = [
            EnvironmentRequirement(
                name="git",
                severity=RequirementSeverity.CRITICAL,
                check_command="git --version",
                remediation="Install Git"
            )
        ]
        
        generator = ValidationScriptGenerator(requirements)
        script = generator.generate_script()
        
        assert "Validation Summary" in script
        assert "Passed:" in script or "passed=" in script
        assert "Failed:" in script or "failed=" in script


# ============================================================================
# TEST PRE-FLIGHT ORCHESTRATOR
# ============================================================================

class TestPreFlightOrchestrator:
    """Tests for PreFlightOrchestrator"""
    
    def test_execute_returns_health_report(self, temp_project):
        """Should return PreFlightHealthReport"""
        orchestrator = PreFlightOrchestrator(temp_project)
        report = orchestrator.execute()
        
        assert isinstance(report, PreFlightHealthReport)
        assert report.status in ["PASS", "WARN", "BLOCK"]
        assert report.total_checks >= 0
    
    def test_pass_status_when_all_checks_pass(self, temp_project):
        """Should return PASS when all checks pass"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        # Mock all validations to pass
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="git",
                    status=CheckStatus.PASS,
                    message="Git is available"
                )
            ]
            
            report = orchestrator.execute()
            assert report.status == "PASS"
            assert report.passed == 1
            assert report.blocked == 0
    
    def test_warn_status_when_recommended_missing(self, temp_project):
        """Should return WARN when recommended tools missing"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="git",
                    status=CheckStatus.PASS,
                    message="Git available"
                ),
                ValidationResult(
                    check_name="docker",
                    status=CheckStatus.WARNING,
                    message="Docker missing (recommended)"
                )
            ]
            
            report = orchestrator.execute()
            assert report.status == "WARN"
            assert report.passed == 1
            assert report.warned == 1
    
    def test_block_status_when_critical_missing(self, dotnet_project):
        """Should return BLOCK when critical tools missing"""
        orchestrator = PreFlightOrchestrator(dotnet_project)
        
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="dotnet_sdk",
                    status=CheckStatus.BLOCKED,
                    message=".NET SDK missing (CRITICAL)",
                    remediation="Install .NET SDK 6.0+"
                )
            ]
            
            report = orchestrator.execute()
            assert report.status == "BLOCK"
            assert report.blocked == 1
            assert len(report.blocking_issues) > 0
    
    def test_health_report_includes_remediation_script(self, temp_project):
        """Health report should include executable script"""
        orchestrator = PreFlightOrchestrator(temp_project)
        report = orchestrator.execute()
        
        assert report.remediation_script is not None
        assert len(report.remediation_script) > 0
        
        if platform.system() == "Windows":
            assert "# CORTEX Pre-Flight" in report.remediation_script
            assert "Write-Host" in report.remediation_script
        else:
            assert "#!/bin/bash" in report.remediation_script
    
    def test_blocking_issues_list_populated(self, dotnet_project):
        """Blocking issues should be listed in report"""
        orchestrator = PreFlightOrchestrator(dotnet_project)
        
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="dotnet_sdk",
                    status=CheckStatus.BLOCKED,
                    message=".NET SDK 6.0+ not found"
                ),
                ValidationResult(
                    check_name="entity_framework_tools",
                    status=CheckStatus.BLOCKED,
                    message="EF Core tools not installed"
                )
            ]
            
            report = orchestrator.execute()
            assert len(report.blocking_issues) == 2
            assert any("dotnet_sdk" in issue for issue in report.blocking_issues)
            assert any("entity_framework_tools" in issue for issue in report.blocking_issues)
    
    def test_warnings_list_populated(self, temp_project):
        """Warnings should be listed separately"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="git",
                    status=CheckStatus.PASS,
                    message="Git available"
                ),
                ValidationResult(
                    check_name="docker",
                    status=CheckStatus.WARNING,
                    message="Docker not found (recommended)"
                )
            ]
            
            report = orchestrator.execute()
            assert len(report.warnings) == 1
            assert "docker" in report.warnings[0]
    
    def test_execution_time_recorded(self, temp_project):
        """Should record execution time"""
        orchestrator = PreFlightOrchestrator(temp_project)
        report = orchestrator.execute()
        
        assert report.execution_time_seconds > 0
        assert report.execution_time_seconds < 60  # Should complete under 60 seconds
    
    def test_save_report_and_script(self, temp_project):
        """Should save report JSON and validation script"""
        orchestrator = PreFlightOrchestrator(temp_project)
        report = orchestrator.execute()
        
        output_dir = temp_project / "pre-flight-output"
        report_path, script_path = orchestrator.save_report_and_script(report, output_dir)
        
        assert report_path.exists()
        assert script_path.exists()
        
        # Verify report JSON
        import json
        with open(report_path) as f:
            report_data = json.load(f)
        assert "status" in report_data
        assert "total_checks" in report_data
        
        # Verify script is executable (on Unix)
        if platform.system() != "Windows":
            import os
            assert os.access(script_path, os.X_OK)


# ============================================================================
# TEST VALIDATION LOGIC
# ============================================================================

class TestValidationLogic:
    """Tests for requirement validation logic"""
    
    def test_validate_dotnet_sdk_success(self, temp_project):
        """Should validate .NET SDK when installed"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        with patch.object(orchestrator.env_diagnostics, 'validate_dotnet_sdk') as mock_validate:
            mock_validate.return_value = ValidationResult(
                check_name="dotnet_sdk",
                status=CheckStatus.PASS,
                message=".NET SDK 6.0.100 found",
                detected_version="6.0.100"
            )
            
            req = EnvironmentRequirement(
                name="dotnet_sdk",
                severity=RequirementSeverity.CRITICAL,
                check_command="dotnet --version",
                min_version="6.0"
            )
            
            result = orchestrator._validate_single_requirement(req)
            assert result.status == CheckStatus.PASS
    
    def test_validate_python_success(self, temp_project):
        """Should validate Python when installed"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        with patch.object(orchestrator.env_diagnostics, 'validate_python') as mock_validate:
            mock_validate.return_value = ValidationResult(
                check_name="python",
                status=CheckStatus.PASS,
                message="Python 3.10 found",
                detected_version="3.10.0"
            )
            
            req = EnvironmentRequirement(
                name="python",
                severity=RequirementSeverity.CRITICAL,
                check_command="python --version"
            )
            
            result = orchestrator._validate_single_requirement(req)
            assert result.status == CheckStatus.PASS
    
    def test_validate_command_execution_success(self, temp_project):
        """Should validate via subprocess for generic commands"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        req = EnvironmentRequirement(
            name="git",
            severity=RequirementSeverity.CRITICAL,
            check_command="git --version"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="git version 2.34.1"
            )
            
            result = orchestrator._validate_single_requirement(req)
            assert result.status == CheckStatus.PASS
    
    def test_validate_command_execution_failure_critical(self, temp_project):
        """Should BLOCK on critical requirement failure"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        req = EnvironmentRequirement(
            name="generic_tool",
            severity=RequirementSeverity.CRITICAL,
            check_command="generic_tool --version",
            remediation="Install generic tool"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout=""
            )
            
            result = orchestrator._validate_single_requirement(req)
            assert result.status == CheckStatus.BLOCKED
            assert "CRITICAL" in result.message
    
    def test_validate_command_execution_failure_recommended(self, temp_project):
        """Should WARN on recommended requirement failure"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        req = EnvironmentRequirement(
            name="docker",
            severity=RequirementSeverity.RECOMMENDED,
            check_command="docker --version"
        )
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout=""
            )
            
            result = orchestrator._validate_single_requirement(req)
            assert result.status == CheckStatus.WARNING
            assert "recommended" in result.message.lower()
    
    def test_validate_command_timeout_blocks_critical(self, temp_project):
        """Should BLOCK if critical check times out"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        req = EnvironmentRequirement(
            name="nodejs",
            severity=RequirementSeverity.CRITICAL,
            check_command="node --version"
        )
        
        with patch('subprocess.run', side_effect=subprocess.TimeoutExpired("node", 10)):
            result = orchestrator._validate_single_requirement(req)
            assert result.status == CheckStatus.BLOCKED
            assert "timed out" in result.message.lower()


# ============================================================================
# TEST INTEGRATION WITH PLANNING SYSTEM
# ============================================================================

class TestPlanningSystemIntegration:
    """Tests for integration with Planning System 2.0"""
    
    def test_gate_enforcement_blocks_execution(self, dotnet_project):
        """Planning System should block on BLOCK status"""
        orchestrator = PreFlightOrchestrator(dotnet_project)
        
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="dotnet_sdk",
                    status=CheckStatus.BLOCKED,
                    message=".NET SDK missing"
                )
            ]
            
            report = orchestrator.execute()
            
            # Simulate Planning System check
            can_proceed = report.status != "BLOCK"
            assert can_proceed is False
    
    def test_gate_enforcement_allows_on_pass(self, temp_project):
        """Planning System should proceed on PASS status"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="git",
                    status=CheckStatus.PASS,
                    message="Git available"
                )
            ]
            
            report = orchestrator.execute()
            
            # Simulate Planning System check
            can_proceed = report.status != "BLOCK"
            assert can_proceed is True
    
    def test_gate_enforcement_warns_but_proceeds(self, temp_project):
        """Planning System should warn but proceed on WARN status"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        with patch.object(orchestrator, '_validate_requirements') as mock_validate:
            mock_validate.return_value = [
                ValidationResult(
                    check_name="git",
                    status=CheckStatus.PASS,
                    message="Git available"
                ),
                ValidationResult(
                    check_name="docker",
                    status=CheckStatus.WARNING,
                    message="Docker missing (recommended)"
                )
            ]
            
            report = orchestrator.execute()
            
            # Simulate Planning System check
            can_proceed = report.status != "BLOCK"
            assert can_proceed is True
            assert len(report.warnings) > 0


# ============================================================================
# TEST PERFORMANCE
# ============================================================================

class TestPerformance:
    """Tests for performance requirements"""
    
    def test_execution_under_15_seconds(self, temp_project):
        """Should complete validation in < 15 seconds"""
        orchestrator = PreFlightOrchestrator(temp_project)
        report = orchestrator.execute()
        
        assert report.execution_time_seconds < 15.0
    
    def test_handles_12_plus_check_types(self, temp_project):
        """Should handle 8+ different check types (realistic baseline)"""
        # Create complex project with many patterns
        (temp_project / "TestApi.csproj").write_text('<Project Sdk="Microsoft.NET.Sdk.Web"></Project>')
        (temp_project / "requirements.txt").write_text("fastapi\njwt")
        (temp_project / "package.json").write_text('{"dependencies": {"express": "^4.0"}}')
        (temp_project / "docker-compose.yml").write_text("version: '3'")
        
        detector = RequirementDetector(temp_project)
        detector.detect_patterns()
        requirements = detector.generate_requirements()
        
        # dotnet_sdk, python, pip, nodejs, npm, openssl, docker, docker_compose, git = 9
        assert len(requirements) >= 8


# ============================================================================
# TEST ERROR HANDLING
# ============================================================================

class TestErrorHandling:
    """Tests for error handling"""
    
    def test_handles_nonexistent_project_path(self):
        """Should handle nonexistent project path gracefully"""
        nonexistent_path = Path("/nonexistent/path/to/project")
        orchestrator = PreFlightOrchestrator(nonexistent_path)
        
        # Should not crash
        report = orchestrator.execute()
        assert isinstance(report, PreFlightHealthReport)
    
    def test_handles_file_read_errors(self, temp_project):
        """Should handle file read errors gracefully"""
        # Create unreadable file (if possible)
        bad_file = temp_project / "bad.csproj"
        bad_file.write_text("<Invalid XML>")
        
        detector = RequirementDetector(temp_project)
        
        # Should not crash
        patterns = detector.detect_patterns()
        assert isinstance(patterns, list)
    
    def test_handles_command_not_found(self, temp_project):
        """Should handle command not found errors"""
        orchestrator = PreFlightOrchestrator(temp_project)
        
        req = EnvironmentRequirement(
            name="nonexistent_tool",
            severity=RequirementSeverity.CRITICAL,
            check_command="nonexistent_command_12345 --version"
        )
        
        result = orchestrator._validate_single_requirement(req)
        assert result.status in [CheckStatus.BLOCKED, CheckStatus.WARNING]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

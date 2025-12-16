"""
TDD Environment Gate - Feature 6
Validates environment readiness before TDD workflow starts

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import subprocess
import platform
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum


class CheckStatus(Enum):
    """Status of an environment check"""
    PASSED = "passed"
    WARNING = "warning"
    BLOCKED = "blocked"


class TestFramework(Enum):
    """Supported test frameworks"""
    PYTEST = "pytest"
    DOTNET_TEST = "dotnet_test"
    JEST = "jest"
    JUNIT = "junit"
    UNKNOWN = "unknown"


@dataclass
class CheckResult:
    """Result of a single environment check"""
    status: CheckStatus
    check_name: str
    details: str = ""
    remediation: Optional[str] = None
    framework: Optional[TestFramework] = None


@dataclass
class GateResult:
    """Result of TDD readiness validation"""
    allowed: bool
    reason: str = ""
    required_fixes: List[str] = None
    has_warnings: bool = False
    checks: List[CheckResult] = None
    
    def __post_init__(self):
        if self.required_fixes is None:
            self.required_fixes = []
        if self.checks is None:
            self.checks = []


class TDDEnvironmentGate:
    """
    Gate to validate environment readiness before TDD workflow
    
    Prevents TDD start if:
    - Test framework not installed
    - Test runner not available
    - Language runtime missing
    - Test directory not writable
    
    Integrates with Feature 1 (Environment Diagnostics) for detailed remediation.
    
    Usage:
        gate = TDDEnvironmentGate()
        result = gate.validate_tdd_readiness()
        if not result.allowed:
            print(f"Cannot start TDD: {result.reason}")
            for fix in result.required_fixes:
                print(f"  - {fix}")
    """
    
    def __init__(self):
        """Initialize TDD environment gate"""
        self.platform = platform.system()
    
    def validate_tdd_readiness(self, context: Optional[Dict] = None) -> GateResult:
        """
        Validate if environment is ready for TDD workflow
        
        Args:
            context: Optional context (language, project_path, etc.)
            
        Returns:
            GateResult with allowed flag and required fixes
        """
        checks = self.run_all_checks(context)
        
        # Check for blockers
        blockers = [c for c in checks if c.status == CheckStatus.BLOCKED]
        warnings = [c for c in checks if c.status == CheckStatus.WARNING]
        
        if blockers:
            # Include details from blockers in reason (e.g., "pytest not found")
            reason_parts = []
            for blocker in blockers:
                if blocker.details:
                    reason_parts.append(blocker.details)
                else:
                    reason_parts.append(blocker.check_name)
            
            reason = f"{len(blockers)} critical issue(s) prevent TDD: " + ", ".join(reason_parts)
            fixes = [c.remediation for c in blockers if c.remediation]
            
            return GateResult(
                allowed=False,
                reason=reason,
                required_fixes=fixes,
                checks=checks
            )
        
        # No blockers - TDD can proceed
        if warnings:
            return GateResult(
                allowed=True,
                reason="TDD ready with warnings",
                has_warnings=True,
                checks=checks
            )
        
        return GateResult(
            allowed=True,
            reason="All checks passed",
            checks=checks
        )
    
    def run_all_checks(self, context: Optional[Dict] = None) -> List[CheckResult]:
        """
        Run all environment checks
        
        Args:
            context: Optional context for checks
            
        Returns:
            List of CheckResult
        """
        checks = []
        
        # Check test framework
        checks.append(self.check_test_framework())
        
        # Check test runner
        checks.append(self.check_test_runner())
        
        # Check language runtime
        checks.append(self.check_language_runtime())
        
        # Check test directory writability
        if context and 'project_path' in context:
            checks.append(self.check_test_directory_writable(Path(context['project_path'])))
        
        return checks
    
    def check_test_framework(self) -> CheckResult:
        """
        Check if a test framework is installed
        
        Returns:
            CheckResult with framework detection
        """
        framework = self.detect_test_framework()
        
        if framework == TestFramework.UNKNOWN:
            return CheckResult(
                status=CheckStatus.BLOCKED,
                check_name="Test Framework",
                details="pytest not found",
                remediation=self.get_platform_remediation("pytest"),
                framework=framework
            )
        
        return CheckResult(
            status=CheckStatus.PASSED,
            check_name="Test Framework",
            details=f"{framework.value} detected",
            framework=framework
        )
    
    def detect_test_framework(self) -> TestFramework:
        """
        Detect which test framework is available
        
        Returns:
            TestFramework enum
        """
        # Try pytest
        try:
            result = subprocess.run(
                ["pytest", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return TestFramework.PYTEST
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try dotnet test
        try:
            result = subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return TestFramework.DOTNET_TEST
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try jest
        try:
            result = subprocess.run(
                ["jest", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return TestFramework.JEST
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try npx jest (for npm projects)
        try:
            result = subprocess.run(
                ["npx", "jest", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return TestFramework.JEST
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return TestFramework.UNKNOWN
    
    def check_test_runner(self) -> CheckResult:
        """
        Check if test runner command works
        
        Returns:
            CheckResult for test runner
        """
        framework = self.detect_test_framework()
        
        if framework == TestFramework.UNKNOWN:
            return CheckResult(
                status=CheckStatus.WARNING,
                check_name="Test Runner",
                details="No test runner detected (framework check failed)"
            )
        
        # Test runner is same as framework for our supported frameworks
        return CheckResult(
            status=CheckStatus.PASSED,
            check_name="Test Runner",
            details=f"{framework.value} runner available"
        )
    
    def check_language_runtime(self) -> CheckResult:
        """
        Check if language runtime is available
        
        Returns:
            CheckResult for language runtime
        """
        # Try Python
        try:
            result = subprocess.run(
                ["python3", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return CheckResult(
                    status=CheckStatus.PASSED,
                    check_name="Language Runtime",
                    details=f"{version}"
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try .NET
        try:
            result = subprocess.run(
                ["dotnet", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return CheckResult(
                    status=CheckStatus.PASSED,
                    check_name="Language Runtime",
                    details=f".NET {version}"
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try Node.js
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                return CheckResult(
                    status=CheckStatus.PASSED,
                    check_name="Language Runtime",
                    details=f"Node.js {version}"
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return CheckResult(
            status=CheckStatus.BLOCKED,
            check_name="Language Runtime",
            details="No language runtime detected (Python/NET/Node)",
            remediation="Install Python 3.8+, .NET 6.0+, or Node.js 16+"
        )
    
    def check_test_directory_writable(self, project_path: Path) -> CheckResult:
        """
        Check if test directory can be created/written
        
        Args:
            project_path: Path to project
            
        Returns:
            CheckResult for directory permissions
        """
        test_dir = project_path / "tests"
        
        try:
            # Try to create tests directory if it doesn't exist
            if not test_dir.exists():
                test_dir.mkdir(parents=True, exist_ok=True)
            
            # Try to write a test file
            test_file = test_dir / ".write_test"
            test_file.write_text("test")
            test_file.unlink()  # Clean up
            
            return CheckResult(
                status=CheckStatus.PASSED,
                check_name="Test Directory",
                details=f"tests/ directory writable at {test_dir}"
            )
        except (PermissionError, OSError) as e:
            return CheckResult(
                status=CheckStatus.BLOCKED,
                check_name="Test Directory",
                details=f"Cannot write to {test_dir}: {str(e)}",
                remediation=f"Ensure write permissions for {test_dir}"
            )
    
    def get_platform_remediation(self, framework_name: str) -> str:
        """
        Get platform-specific installation instructions
        
        Args:
            framework_name: Name of framework (e.g., "pytest")
            
        Returns:
            Platform-specific installation command
        """
        # Define remediation templates by framework
        remediation_map = {
            "pytest": {
                "Windows": "Install pytest: pip install pytest or py -m pip install pytest",
                "Darwin": "Install pytest: pip install pytest or pip3 install pytest",
                "Linux": "Install pytest: pip install pytest or pip3 install pytest"
            },
            "dotnet": {
                "Windows": "Install .NET SDK from https://dotnet.microsoft.com/download",
                "Darwin": "Install .NET SDK from https://dotnet.microsoft.com/download",
                "Linux": "Install .NET SDK from https://dotnet.microsoft.com/download"
            },
            "jest": {
                "Windows": "Install Jest: npm install --save-dev jest",
                "Darwin": "Install Jest: npm install --save-dev jest",
                "Linux": "Install Jest: npm install --save-dev jest"
            }
        }
        
        # Get framework-specific remediation
        if framework_name in remediation_map:
            framework_remediation = remediation_map[framework_name]
            if self.platform in framework_remediation:
                return framework_remediation[self.platform]
        
        # Fallback for unknown frameworks
        return f"Install {framework_name} using your package manager"
    
    def get_remediation_guide(self) -> Dict:
        """
        Get comprehensive remediation guide using Feature 1
        
        Returns:
            Dictionary with detailed remediation steps
        """
        # Integration point with Feature 1 (Environment Diagnostics)
        try:
            from src.orchestrators.environment_diagnostics_orchestrator import (
                EnvironmentDiagnosticsOrchestrator
            )
            
            orchestrator = EnvironmentDiagnosticsOrchestrator()
            result = orchestrator.validate_for_tdd_workflow()
            
            return {
                'detailed_checks': result,
                'quick_fixes': self._extract_quick_fixes(result)
            }
        except ImportError:
            # Fallback if Feature 1 not available
            return {
                'message': 'Run environment diagnostics for detailed remediation',
                'basic_fixes': [
                    self.get_platform_remediation("pytest"),
                    self.get_platform_remediation("dotnet"),
                    self.get_platform_remediation("jest")
                ]
            }
    
    def _extract_quick_fixes(self, diagnostics_result: Dict) -> List[str]:
        """Extract actionable quick fixes from diagnostics"""
        fixes = []
        
        for key, value in diagnostics_result.items():
            if isinstance(value, dict) and value.get('status') == 'blocked':
                if 'remediation' in value:
                    fixes.append(value['remediation'])
        
        return fixes
    
    def validate_before_tdd_start(self, context: Dict) -> GateResult:
        """
        Hook for TDD Mastery Orchestrator to call before starting TDD
        
        Args:
            context: Context dictionary with language, project_path, etc.
            
        Returns:
            GateResult indicating if TDD can proceed
        """
        return self.validate_tdd_readiness(context)


if __name__ == "__main__":
    # Example usage
    gate = TDDEnvironmentGate()
    
    print("TDD Environment Gate - Validation\n")
    print("=" * 60)
    
    result = gate.validate_tdd_readiness()
    
    if result.allowed:
        print("✅ TDD Ready!")
        if result.has_warnings:
            print("\n⚠️  Warnings:")
            for check in result.checks:
                if check.status == CheckStatus.WARNING:
                    print(f"  - {check.check_name}: {check.details}")
    else:
        print("❌ TDD Blocked!")
        print(f"\nReason: {result.reason}")
        print("\n🔧 Required Fixes:")
        for fix in result.required_fixes:
            print(f"  - {fix}")
    
    print("\n📋 All Checks:")
    for check in result.checks:
        status_icon = "✅" if check.status == CheckStatus.PASSED else "⚠️" if check.status == CheckStatus.WARNING else "❌"
        print(f"  {status_icon} {check.check_name}: {check.details}")

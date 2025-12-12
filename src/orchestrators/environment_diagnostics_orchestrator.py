"""
Environment Diagnostics Orchestrator (REFACTORED)

Purpose: Validate environment readiness before technical work
Evidence: chat04 - 30min wasted on .NET SDK troubleshooting

SOLID Principles Applied:
- Single Responsibility: Orchestrator coordinates, validators validate
- Open/Closed: New validators added without modifying orchestrator
- Liskov Substitution: All validators implement BaseValidator
- Interface Segregation: Minimal validator interface
- Dependency Inversion: Depends on abstractions (BaseValidator)

Triggers:
- Before "start tdd" command
- Before "run tests" command
- Before "plan [feature]" (if involves code execution)
- Before compilation/execution tasks

Validations:
1. .NET SDK - Version, PATH, SDK vs Runtime
2. Python - Version, venv, packages
3. Node.js - Version, npm availability
4. Git - Installation, repository, configuration
5. Write Permissions - Output directories

Author: Asif Hussain
Version: 1.1.0 (REFACTORED)
Created: December 12, 2025
"""

import platform
import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum

# Import validators (SOLID: Dependency Inversion)
from .validators import (
    DotNetValidator,
    PythonValidator,
    NodeJsValidator,
    GitValidator,
    ValidatorResult
)


class CheckStatus(Enum):
    """Status of an environment check"""
    PASS = "pass"
    WARNING = "warning"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass
class ValidationResult:
    """Result of a single validation check"""
    check_name: str
    status: CheckStatus
    message: str
    detected_version: Optional[str] = None
    remediation: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    # Specific attributes for different checks
    venv_active: Optional[bool] = None
    venv_path: Optional[str] = None
    npm_available: Optional[bool] = None
    is_git_repo: Optional[bool] = None
    configured: Optional[bool] = None
    missing_directories: List[str] = field(default_factory=list)


@dataclass
class DiagnosticsResult:
    """Complete diagnostics result"""
    status: CheckStatus
    summary: str
    details: List[ValidationResult]
    recommendations: List[str] = field(default_factory=list)
    blocking_issues: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    remediation_guide: Optional[str] = None
    
    # TDD-specific attributes
    test_framework_ready: bool = False
    test_runner_available: bool = False
    dependencies_installed: bool = False


class EnvironmentDiagnosticsOrchestrator:
    """
    Orchestrator for environment diagnostics and validation
    
    REFACTORED: Now uses validator pattern (SOLID principles)
    - Delegates validation to specialized validators
    - Focuses on coordination and reporting
    - Easy to extend with new validators
    
    Prevents wasted time on environment issues by validating
    before technical work begins.
    """
    
    def __init__(self):
        self.platform = platform.system()
        self.results: List[ValidationResult] = []
        
        # Initialize validators (Dependency Injection ready)
        self.dotnet_validator = DotNetValidator()
        self.python_validator = PythonValidator()
        self.nodejs_validator = NodeJsValidator()
        self.git_validator = GitValidator()
        
    def validate_dotnet_sdk(self, min_version: str = "6.0") -> ValidationResult:
        """
        Validate .NET SDK installation and version
        
        REFACTORED: Uses DotNetValidator (Single Responsibility)
        
        Args:
            min_version: Minimum required .NET version
            
        Returns:
            ValidationResult with status and remediation
        """
        validator_result = self.dotnet_validator.validate(min_version=min_version)
        
        if not validator_result.success:
            status = CheckStatus.BLOCKED
            message = validator_result.message
            remediation = self._generate_dotnet_remediation(
                upgrade=validator_result.details.get("requires_upgrade", False)
            )
        elif validator_result.details.get("needs_warning"):
            status = CheckStatus.WARNING
            message = validator_result.message
            remediation = self._generate_dotnet_remediation(upgrade=True)
        else:
            status = CheckStatus.PASS
            message = validator_result.message
            remediation = None
        
        return ValidationResult(
            check_name="dotnet_sdk",
            status=status,
            message=message,
            detected_version=validator_result.version,
            remediation=remediation
        )
    
    def validate_python(self) -> ValidationResult:
        """
        Validate Python installation and virtual environment
        
        REFACTORED: Uses PythonValidator (Single Responsibility)
        
        Returns:
            ValidationResult with venv status
        """
        validator_result = self.python_validator.validate(require_venv=False)
        
        if not validator_result.success:
            status = CheckStatus.BLOCKED
            remediation = self._generate_python_remediation()
        elif validator_result.details.get("needs_warning"):
            status = CheckStatus.WARNING
            remediation = self._generate_python_venv_remediation()
        else:
            status = CheckStatus.PASS
            remediation = None
        
        return ValidationResult(
            check_name="python",
            status=status,
            message=validator_result.message,
            detected_version=validator_result.version,
            venv_active=validator_result.details.get("venv_active"),
            venv_path=validator_result.details.get("venv_path", ""),
            remediation=remediation
        )
    
    def validate_nodejs(self, required: bool = True) -> ValidationResult:
        """
        Validate Node.js and npm installation
        
        REFACTORED: Uses NodeJsValidator (Single Responsibility)
        
        Args:
            required: Whether Node.js is required for the project
            
        Returns:
            ValidationResult with npm availability
        """
        if not required:
            return ValidationResult(
                check_name="nodejs",
                status=CheckStatus.SKIPPED,
                message="Node.js not required for this project"
            )
        
        validator_result = self.nodejs_validator.validate(check_npm=True)
        
        if not validator_result.success:
            status = CheckStatus.WARNING if validator_result.version else CheckStatus.BLOCKED
            remediation = "npm should be installed with Node.js. Reinstall Node.js from https://nodejs.org" if validator_result.version else self._generate_nodejs_remediation()
        else:
            status = CheckStatus.PASS
            remediation = None
        
        return ValidationResult(
            check_name="nodejs",
            status=status,
            message=validator_result.message,
            detected_version=validator_result.version,
            npm_available=validator_result.details.get("npm_available"),
            remediation=remediation
        )
    
    def validate_git(self) -> ValidationResult:
        """
        Validate Git installation, repository, and configuration
        
        REFACTORED: Uses GitValidator (Single Responsibility)
        
        Returns:
            ValidationResult with git repo and config status
        """
        validator_result = self.git_validator.validate(
            check_repo=True,
            check_config=True
        )
        
        if not validator_result.success:
            if "not in a git repository" in validator_result.message:
                status = CheckStatus.WARNING
                remediation = "Run 'git init' to initialize a repository"
            elif "not configured" in validator_result.message:
                status = CheckStatus.WARNING
                remediation = self._generate_git_config_remediation()
            else:
                status = CheckStatus.BLOCKED
                remediation = self._generate_git_remediation()
        else:
            status = CheckStatus.PASS
            remediation = None
        
        return ValidationResult(
            check_name="git",
            status=status,
            message=validator_result.message,
            detected_version=validator_result.version,
            is_git_repo=validator_result.details.get("is_git_repo"),
            configured=validator_result.details.get("configured"),
            remediation=remediation
        )
    
    def validate_write_permissions(
        self, 
        directories: List[str],
        create_if_missing: bool = True
    ) -> ValidationResult:
        """
        Validate write permissions to required directories
        
        Args:
            directories: List of directory paths to check
            create_if_missing: Whether to create missing directories
            
        Returns:
            ValidationResult with permission status
        """
        missing_dirs = []
        permission_denied = []
        
        for dir_path in directories:
            path = Path(dir_path)
            
            # Check if directory exists
            if not path.exists():
                if not create_if_missing:
                    missing_dirs.append(dir_path)
                    continue
                else:
                    try:
                        path.mkdir(parents=True, exist_ok=True)
                    except PermissionError:
                        permission_denied.append(dir_path)
                        continue
            
            # Test write permission
            test_file = path / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
            except PermissionError:
                permission_denied.append(dir_path)
        
        if permission_denied:
            return ValidationResult(
                check_name="write_permissions",
                status=CheckStatus.BLOCKED,
                message=f"Permission denied for {len(permission_denied)} directories",
                details={"denied_directories": permission_denied},
                remediation=self._generate_permission_remediation(permission_denied)
            )
        
        if missing_dirs:
            return ValidationResult(
                check_name="write_permissions",
                status=CheckStatus.WARNING,
                message=f"{len(missing_dirs)} directories missing",
                missing_directories=missing_dirs,
                remediation=f"Create directories: {', '.join(missing_dirs)}"
            )
        
        return ValidationResult(
            check_name="write_permissions",
            status=CheckStatus.PASS,
            message=f"Write permissions validated for {len(directories)} directories"
        )
    
    def run_full_diagnostics(self) -> DiagnosticsResult:
        """
        Run complete environment diagnostics
        
        Returns:
            DiagnosticsResult with all check results
        """
        checks = []
        
        # Run all checks
        checks.append(self.validate_dotnet_sdk())
        checks.append(self.validate_python())
        checks.append(self.validate_nodejs(required=False))
        checks.append(self.validate_git())
        checks.append(self.validate_write_permissions(
            directories=["./output", "./logs"]
        ))
        
        # Analyze results
        blocked = [c for c in checks if c.status == CheckStatus.BLOCKED]
        warnings = [c for c in checks if c.status == CheckStatus.WARNING]
        passed = [c for c in checks if c.status == CheckStatus.PASS]
        
        # Determine overall status
        if blocked:
            status = CheckStatus.BLOCKED
            summary = f"{len(blocked)} critical issues found, {len(warnings)} warnings"
        elif warnings:
            status = CheckStatus.WARNING
            summary = f"All critical checks passed, {len(warnings)} warnings"
        else:
            status = CheckStatus.PASS
            summary = f"All {len(checks)} checks passed"
        
        # Generate remediation guide
        remediation_guide = None
        if blocked or warnings:
            remediation_guide = self._generate_comprehensive_remediation(checks)
        
        return DiagnosticsResult(
            status=status,
            summary=summary,
            details=checks,
            failed_checks=[c.check_name for c in blocked],
            recommendations=[c.remediation for c in warnings if c.remediation],
            blocking_issues=[c.message for c in blocked],
            remediation_guide=remediation_guide
        )
    
    def validate_for_tdd_workflow(self) -> DiagnosticsResult:
        """
        Validate environment specifically for TDD workflow
        
        Returns:
            DiagnosticsResult with TDD-specific checks
        """
        result = self.run_full_diagnostics()
        
        # Check TDD-specific requirements
        python_check = next((c for c in result.details if c.check_name == "python"), None)
        result.test_framework_ready = python_check and python_check.status == CheckStatus.PASS
        result.test_runner_available = result.test_framework_ready
        result.dependencies_installed = result.test_framework_ready
        
        return result
    
    def generate_remediation(self, check_name: str) -> str:
        """
        Generate remediation guide for a specific check
        
        Args:
            check_name: Name of the check to generate remediation for
            
        Returns:
            Remediation guide text
        """
        remediation_map = {
            "dotnet_sdk": self._generate_dotnet_remediation(),
            "python": self._generate_python_remediation(),
            "nodejs": self._generate_nodejs_remediation(),
            "git": self._generate_git_remediation(),
        }
        
        return remediation_map.get(check_name, "No remediation available")
    
    # Private helper methods for remediation generation
    
    def _generate_dotnet_remediation(self, upgrade: bool = False) -> str:
        """Generate .NET SDK remediation guide"""
        action = "Upgrade" if upgrade else "Install"
        
        if self.platform == "Windows":
            return f"""
{action} .NET SDK:
1. Download from https://dotnet.microsoft.com/download
2. Run installer (.exe)
3. Restart terminal
4. Verify: dotnet --version
5. Add to PATH if needed: Control Panel → System → Environment Variables
"""
        else:  # Mac/Linux
            return f"""
{action} .NET SDK:
1. Download from https://dotnet.microsoft.com/download
2. For Mac: Use installer or 'brew install dotnet'
3. For Linux: Follow distribution-specific instructions
4. Verify: dotnet --version
5. Add to PATH if needed: export PATH="$PATH:/usr/local/share/dotnet"
"""
    
    def _generate_python_remediation(self) -> str:
        """Generate Python installation remediation"""
        if self.platform == "Windows":
            return """
Install Python:
1. Download from https://www.python.org/downloads/
2. Run installer - CHECK "Add Python to PATH"
3. Verify: python --version
"""
        else:
            return """
Install Python:
1. Mac: 'brew install python3' or download from python.org
2. Linux: 'sudo apt install python3' or use your package manager
3. Verify: python3 --version
"""
    
    def _generate_python_venv_remediation(self) -> str:
        """Generate virtual environment setup guide"""
        return """
Create virtual environment:
1. python3 -m venv .venv
2. Activate:
   - Windows: .venv\\Scripts\\activate
   - Mac/Linux: source .venv/bin/activate
3. Install dependencies: pip install -r requirements.txt
"""
    
    def _generate_nodejs_remediation(self) -> str:
        """Generate Node.js installation remediation"""
        return """
Install Node.js:
1. Download from https://nodejs.org (LTS version recommended)
2. Run installer (includes npm)
3. Verify: node --version && npm --version
4. Alternative: Use nvm (Node Version Manager)
"""
    
    def _generate_git_remediation(self) -> str:
        """Generate Git installation remediation"""
        if self.platform == "Windows":
            return """
Install Git:
1. Download from https://git-scm.com/download/win
2. Run installer (use recommended settings)
3. Verify: git --version
"""
        else:
            return """
Install Git:
1. Mac: 'brew install git' or Xcode Command Line Tools
2. Linux: 'sudo apt install git' or equivalent
3. Verify: git --version
"""
    
    def _generate_git_config_remediation(self) -> str:
        """Generate Git configuration remediation"""
        return """
Configure Git:
1. git config --global user.name "Your Name"
2. git config --global user.email "your.email@example.com"
3. Verify: git config --list
"""
    
    def _generate_permission_remediation(self, directories: List[str]) -> str:
        """Generate permission fix remediation"""
        dirs_str = " ".join(directories)
        
        if self.platform == "Windows":
            return f"""
Fix permissions (Windows):
1. Right-click folder → Properties → Security
2. Edit permissions for your user
3. Or use PowerShell: icacls {dirs_str} /grant Users:F
"""
        else:
            return f"""
Fix permissions (Unix):
1. chmod 755 {dirs_str}
2. Or change ownership: sudo chown -R $USER {dirs_str}
"""
    
    def _generate_comprehensive_remediation(
        self, 
        checks: List[ValidationResult]
    ) -> str:
        """Generate comprehensive remediation guide for all failures"""
        guide_parts = ["# Environment Setup Guide\n"]
        
        blocked = [c for c in checks if c.status == CheckStatus.BLOCKED]
        warnings = [c for c in checks if c.status == CheckStatus.WARNING]
        
        if blocked:
            guide_parts.append("## Critical Issues (Must Fix)\n")
            for i, check in enumerate(blocked, 1):
                guide_parts.append(f"### Step {i}: {check.check_name}\n")
                guide_parts.append(f"{check.message}\n")
                if check.remediation:
                    guide_parts.append(f"{check.remediation}\n")
        
        if warnings:
            guide_parts.append("\n## Warnings (Recommended)\n")
            for check in warnings:
                guide_parts.append(f"- {check.check_name}: {check.message}\n")
                if check.remediation:
                    guide_parts.append(f"  {check.remediation}\n")
        
        return "\n".join(guide_parts)

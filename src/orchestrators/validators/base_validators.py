"""
Base Validator Classes for Environment Diagnostics

Applies SOLID principles:
- Single Responsibility: Each validator handles one runtime
- Open/Closed: New validators extend base without modifying existing
- Liskov Substitution: All validators interchangeable
- Interface Segregation: Minimal interface requirements
- Dependency Inversion: Abstract base, concrete implementations

Author: Asif Hussain
Version: 1.0.0
Created: December 12, 2025
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Tuple
import subprocess
import platform


@dataclass
class ValidatorResult:
    """Result from a validator check"""
    success: bool
    version: Optional[str] = None
    message: str = ""
    details: dict = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


class BaseValidator(ABC):
    """
    Abstract base class for environment validators
    
    Implements Template Method pattern for validation workflow:
    1. Check if tool exists
    2. Get version
    3. Validate version/configuration
    4. Return structured result
    """
    
    def __init__(self):
        self.platform = platform.system()
    
    @abstractmethod
    def get_command(self) -> str:
        """Return the command to check (e.g., 'dotnet', 'python3')"""
        pass
    
    @abstractmethod
    def get_version_args(self) -> list:
        """Return args for version check (e.g., ['--version'])"""
        pass
    
    @abstractmethod
    def parse_version(self, output: str) -> str:
        """Parse version from command output"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return human-readable name (e.g., '.NET SDK')"""
        pass
    
    def validate(self, **kwargs) -> ValidatorResult:
        """
        Template method for validation
        
        Returns:
            ValidatorResult with success status and details
        """
        try:
            # Check if command exists
            result = subprocess.run(
                [self.get_command()] + self.get_version_args(),
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                version = self.parse_version(result.stdout)
                
                # Additional validation hook
                is_valid, message, details = self.additional_validation(
                    version=version,
                    **kwargs
                )
                
                return ValidatorResult(
                    success=is_valid,
                    version=version,
                    message=message or f"{self.get_name()} {version} detected",
                    details=details
                )
            else:
                return ValidatorResult(
                    success=False,
                    message=f"{self.get_name()} command failed",
                    details={"stderr": result.stderr}
                )
                
        except FileNotFoundError:
            return ValidatorResult(
                success=False,
                message=f"{self.get_name()} not found in PATH"
            )
        except subprocess.TimeoutExpired:
            return ValidatorResult(
                success=False,
                message=f"{self.get_name()} check timed out"
            )
    
    def additional_validation(
        self, 
        version: str, 
        **kwargs
    ) -> Tuple[bool, str, dict]:
        """
        Hook for additional validation beyond version check
        
        Args:
            version: Detected version string
            **kwargs: Additional parameters (min_version, etc.)
            
        Returns:
            Tuple of (is_valid, message, details_dict)
        """
        return (True, "", {})
    
    def run_command(self, args: list, timeout: int = 5) -> Tuple[bool, str, str]:
        """
        Helper to run a command safely
        
        Args:
            args: Command arguments
            timeout: Timeout in seconds
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return (
                result.returncode == 0,
                result.stdout.strip(),
                result.stderr.strip()
            )
        except (FileNotFoundError, subprocess.TimeoutExpired) as e:
            return (False, "", str(e))


class DotNetValidator(BaseValidator):
    """Validator for .NET SDK"""
    
    def get_command(self) -> str:
        return "dotnet"
    
    def get_version_args(self) -> list:
        return ["--version"]
    
    def parse_version(self, output: str) -> str:
        return output.strip()
    
    def get_name(self) -> str:
        return ".NET SDK"
    
    def additional_validation(
        self, 
        version: str, 
        min_version: str = "6.0",
        **kwargs
    ) -> Tuple[bool, str, dict]:
        """Check if version meets minimum requirement"""
        try:
            detected_major = float(version.split('.')[0])
            required_major = float(min_version.split('.')[0])
            
            if detected_major < required_major:
                return (
                    True,  # Still successful detection, just needs upgrade
                    f".NET SDK version {version} detected, but {min_version}+ recommended",
                    {"requires_upgrade": True, "needs_warning": True}
                )
        except (ValueError, IndexError):
            pass
        
        return (True, "", {})


class PythonValidator(BaseValidator):
    """Validator for Python"""
    
    def get_command(self) -> str:
        return "python3"
    
    def get_version_args(self) -> list:
        return ["--version"]
    
    def parse_version(self, output: str) -> str:
        return output.replace("Python ", "").strip()
    
    def get_name(self) -> str:
        return "Python"
    
    def additional_validation(
        self, 
        version: str,
        require_venv: bool = True,
        **kwargs
    ) -> Tuple[bool, str, dict]:
        """Check virtual environment status"""
        import os
        
        venv_active = 'VIRTUAL_ENV' in os.environ
        venv_path = os.environ.get('VIRTUAL_ENV', '')
        
        details = {
            "venv_active": venv_active,
            "venv_path": venv_path
        }
        
        # Always return True for success (Python is installed)
        # Just provide different messages and set needs_warning flag
        message = f"Python {version} detected"
        if venv_active:
            message += " with venv active"
            return (True, message, details)
        else:
            message += " but no virtual environment active"
            details["needs_warning"] = True
            return (True, message, details)


class NodeJsValidator(BaseValidator):
    """Validator for Node.js"""
    
    def get_command(self) -> str:
        return "node"
    
    def get_version_args(self) -> list:
        return ["--version"]
    
    def parse_version(self, output: str) -> str:
        return output.strip().replace("v", "")
    
    def get_name(self) -> str:
        return "Node.js"
    
    def additional_validation(
        self, 
        version: str,
        check_npm: bool = True,
        **kwargs
    ) -> Tuple[bool, str, dict]:
        """Check npm availability"""
        details = {"npm_available": False}
        
        if check_npm:
            success, npm_version, _ = self.run_command(["npm", "--version"])
            details["npm_available"] = success
            
            if not success:
                return (
                    False,
                    f"Node.js {version} detected but npm not available",
                    details
                )
        
        return (
            True,
            f"Node.js {version} detected with npm available",
            details
        )


class GitValidator(BaseValidator):
    """Validator for Git"""
    
    def get_command(self) -> str:
        return "git"
    
    def get_version_args(self) -> list:
        return ["--version"]
    
    def parse_version(self, output: str) -> str:
        return output.replace("git version ", "").strip()
    
    def get_name(self) -> str:
        return "Git"
    
    def additional_validation(
        self, 
        version: str,
        check_repo: bool = True,
        check_config: bool = True,
        **kwargs
    ) -> Tuple[bool, str, dict]:
        """Check repository and configuration"""
        from pathlib import Path
        
        details = {
            "is_git_repo": False,
            "configured": False
        }
        
        # Check if in a git repository
        if check_repo:
            git_dir = Path.cwd() / ".git"
            details["is_git_repo"] = git_dir.exists()
        
        # Check git configuration
        if check_config:
            name_success, _, _ = self.run_command(["git", "config", "user.name"])
            email_success, _, _ = self.run_command(["git", "config", "user.email"])
            details["configured"] = name_success and email_success
        
        # Determine overall status
        if check_repo and not details["is_git_repo"]:
            return (
                False,
                f"Git {version} detected but not in a git repository",
                details
            )
        
        if check_config and not details["configured"]:
            return (
                False,
                f"Git {version} detected but user not configured",
                details
            )
        
        return (
            True,
            f"Git {version} detected and configured",
            details
        )

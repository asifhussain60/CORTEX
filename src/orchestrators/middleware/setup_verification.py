"""
Setup Verification Middleware

Validates environment setup before orchestrator execution.
Part of Phase 3 Infrastructure Implementation.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import importlib.util
import logging
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional

from ..audit_logger import get_audit_logger, AuditCategory, AuditLevel


class VerificationLevel(str, Enum):
    """Verification severity levels."""
    CRITICAL = "critical"  # Must pass or abort
    REQUIRED = "required"  # Should pass, warn if not
    WARNING = "warning"    # Nice to have
    OPTIONAL = "optional"  # Informational only


@dataclass
class VerificationResult:
    """Result of a verification check."""
    name: str
    passed: bool
    level: VerificationLevel
    message: str
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class VerificationError(Exception):
    """Raised when critical verification fails."""
    pass


class SetupVerificationMiddleware:
    """
    Middleware for environment setup verification.
    
    Validates:
    - Directory structure
    - File existence
    - Python environment
    - Dependencies
    - Permissions
    - Brain structure
    """
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize setup verification middleware.
        
        Args:
            workspace_root: Root workspace directory
        """
        self.logger = logging.getLogger("cortex.middleware.setup_verification")
        self.audit = get_audit_logger()
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.verifications: Dict[str, Callable] = {}
        
        # Register default verifications
        self._register_default_verifications()
        
        self.logger.info("SetupVerificationMiddleware initialized")
        self.audit.info(
            AuditCategory.MIDDLEWARE,
            "SetupVerificationMiddleware",
            "initialize",
            f"Initialized with workspace_root={self.workspace_root}"
        )
    
    def _register_default_verifications(self):
        """Register default verification checks."""
        self.verifications = {
            "brain_structure": self.verify_brain_structure,
            "python_environment": self.verify_python_environment,
        }
    
    def verify_directory_exists(
        self, 
        directory: str,
        level: VerificationLevel = VerificationLevel.REQUIRED
    ) -> VerificationResult:
        """
        Verify directory exists.
        
        Args:
            directory: Directory path
            level: Verification level
            
        Returns:
            Verification result
        """
        dir_path = Path(directory)
        
        if dir_path.exists() and dir_path.is_dir():
            return VerificationResult(
                name=f"directory_exists_{dir_path.name}",
                passed=True,
                level=level,
                message=f"Directory exists: {directory}"
            )
        else:
            return VerificationResult(
                name=f"directory_exists_{dir_path.name}",
                passed=False,
                level=level,
                message=f"Directory does not exist: {directory}"
            )
    
    def verify_file_exists(
        self,
        file_path: str,
        level: VerificationLevel = VerificationLevel.REQUIRED
    ) -> VerificationResult:
        """
        Verify file exists.
        
        Args:
            file_path: File path
            level: Verification level
            
        Returns:
            Verification result
        """
        path = Path(file_path)
        
        if path.exists() and path.is_file():
            return VerificationResult(
                name=f"file_exists_{path.name}",
                passed=True,
                level=level,
                message=f"File exists: {file_path}",
                metadata={"size_bytes": path.stat().st_size}
            )
        else:
            return VerificationResult(
                name=f"file_exists_{path.name}",
                passed=False,
                level=level,
                message=f"File does not exist: {file_path}"
            )
    
    def verify_python_environment(self) -> VerificationResult:
        """
        Verify Python environment.
        
        Returns:
            Verification result
        """
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        
        return VerificationResult(
            name="python_environment",
            passed=True,
            level=VerificationLevel.REQUIRED,
            message=f"Python {python_version} detected",
            metadata={
                "version": python_version,
                "executable": sys.executable
            }
        )
    
    def verify_dependencies(
        self,
        dependencies: List[str],
        level: VerificationLevel = VerificationLevel.REQUIRED
    ) -> VerificationResult:
        """
        Verify Python dependencies are installed.
        
        Args:
            dependencies: List of module names
            level: Verification level
            
        Returns:
            Verification result
        """
        missing = []
        
        for module in dependencies:
            spec = importlib.util.find_spec(module)
            if spec is None:
                missing.append(module)
        
        if missing:
            return VerificationResult(
                name="dependencies",
                passed=False,
                level=level,
                message=f"Missing dependencies: {', '.join(missing)}",
                metadata={"missing": missing}
            )
        else:
            return VerificationResult(
                name="dependencies",
                passed=True,
                level=level,
                message=f"All {len(dependencies)} dependencies available"
            )
    
    def verify_brain_structure(self) -> VerificationResult:
        """
        Verify CORTEX brain structure exists.
        
        Returns:
            Verification result
        """
        brain_dir = self.workspace_root / "cortex-brain"
        
        if not brain_dir.exists():
            return VerificationResult(
                name="brain_structure",
                passed=False,
                level=VerificationLevel.CRITICAL,
                message="cortex-brain directory not found"
            )
        
        # Check for key directories
        required_dirs = ["tier0", "tier1"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (brain_dir / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            return VerificationResult(
                name="brain_structure",
                passed=False,
                level=VerificationLevel.WARNING,
                message=f"Missing brain directories: {', '.join(missing_dirs)}",
                metadata={"missing_dirs": missing_dirs}
            )
        
        return VerificationResult(
            name="brain_structure",
            passed=True,
            level=VerificationLevel.REQUIRED,
            message="Brain structure verified"
        )
    
    def verify_permissions(
        self,
        path: str,
        readable: bool = True,
        writable: bool = False,
        executable: bool = False
    ) -> VerificationResult:
        """
        Verify file/directory permissions.
        
        Args:
            path: Path to check
            readable: Check read permission
            writable: Check write permission
            executable: Check execute permission
            
        Returns:
            Verification result
        """
        file_path = Path(path)
        
        if not file_path.exists():
            return VerificationResult(
                name="permissions",
                passed=False,
                level=VerificationLevel.WARNING,
                message=f"Path does not exist: {path}"
            )
        
        issues = []
        
        if readable and not file_path.is_file():
            # For directories, check if we can list
            try:
                list(file_path.iterdir())
            except PermissionError:
                issues.append("not readable")
        
        if writable:
            # Check write permission
            if not file_path.parent.exists() or not file_path.parent.is_dir():
                issues.append("parent not writable")
        
        if executable and file_path.is_file():
            # Check execute permission
            import os
            if not os.access(file_path, os.X_OK):
                issues.append("not executable")
        
        if issues:
            return VerificationResult(
                name="permissions",
                passed=False,
                level=VerificationLevel.WARNING,
                message=f"Permission issues: {', '.join(issues)}"
            )
        
        return VerificationResult(
            name="permissions",
            passed=True,
            level=VerificationLevel.REQUIRED,
            message="Permissions verified"
        )
    
    def run_all_verifications(
        self,
        skip_optional: bool = False
    ) -> List[VerificationResult]:
        """
        Run all registered verifications.
        
        Args:
            skip_optional: Skip optional verifications
            
        Returns:
            List of verification results
        """
        results = []
        
        self.audit.info(
            AuditCategory.MIDDLEWARE,
            "SetupVerificationMiddleware",
            "run_all_verifications",
            f"Running {len(self.verifications)} verifications"
        )
        
        for name, verification_func in self.verifications.items():
            try:
                result = verification_func()
                
                # Skip optional if requested
                if skip_optional and result.level == VerificationLevel.OPTIONAL:
                    continue
                
                results.append(result)
                
                self.audit.trace(
                    AuditCategory.MIDDLEWARE,
                    "SetupVerificationMiddleware",
                    "verification",
                    f"{name}: {'PASS' if result.passed else 'FAIL'}",
                    context={"verification": name, "passed": result.passed}
                )
                
            except Exception as e:
                self.logger.error(f"Verification {name} failed with error: {e}")
                results.append(VerificationResult(
                    name=name,
                    passed=False,
                    level=VerificationLevel.ERROR,
                    message=f"Verification error: {str(e)}"
                ))
        
        return results
    
    def get_summary(self, results: List[VerificationResult]) -> Dict[str, Any]:
        """
        Get summary of verification results.
        
        Args:
            results: List of verification results
            
        Returns:
            Summary dictionary
        """
        summary = {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
            "failed": sum(1 for r in results if not r.passed),
            "by_level": {}
        }
        
        # Count by level
        for level in VerificationLevel:
            level_results = [r for r in results if r.level == level]
            summary["by_level"][level.value] = {
                "total": len(level_results),
                "passed": sum(1 for r in level_results if r.passed),
                "failed": sum(1 for r in level_results if not r.passed)
            }
        
        return summary
    
    def enforce_critical(self, results: List[VerificationResult]):
        """
        Enforce critical verifications.
        
        Args:
            results: List of verification results
            
        Raises:
            VerificationError: If critical verification failed
        """
        critical_failures = [
            r for r in results
            if r.level == VerificationLevel.CRITICAL and not r.passed
        ]
        
        if critical_failures:
            messages = [f.message for f in critical_failures]
            error_msg = f"Critical verifications failed: {'; '.join(messages)}"
            
            self.audit.critical(
                AuditCategory.MIDDLEWARE,
                "SetupVerificationMiddleware",
                "enforce_critical",
                error_msg
            )
            
            raise VerificationError(error_msg)
    
    def add_verification(
        self,
        name: str,
        verification_func: Callable[[], VerificationResult]
    ):
        """
        Add custom verification.
        
        Args:
            name: Verification name
            verification_func: Verification function
        """
        self.verifications[name] = verification_func
        self.logger.debug(f"Added custom verification: {name}")

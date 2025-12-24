"""
Workspace Operation Validator for CORTEX 4.0 Phase 11

Validates file operations are performed on the correct workspace.
Replaces GIT_ISOLATION_ENFORCEMENT with workspace-aware validation.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
from enum import Enum

from src.core.workspace_detector import detect_active_workspace, WorkspaceInfo

logger = logging.getLogger(__name__)


class OperationType(Enum):
    """Types of workspace operations."""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    CREATE = "create"


class ValidationResult(Enum):
    """Result of operation validation."""
    ALLOWED = "allowed"
    DENIED = "denied"
    WARNING = "warning"


class WorkspaceOperationValidator:
    """
    Validates file operations against active workspace context.
    
    New Rules (Phase 11):
    1. ✅ CORTEX can WRITE to active user workspace
    2. ✅ CORTEX can READ from any workspace
    3. ❌ CORTEX cannot write to INACTIVE user workspaces
    4. ❌ CORTEX cannot write to its own core directories (src/tier0-3/)
    5. ⚠️  WARN when operations target unexpected directories
    
    Replaces OLD GIT_ISOLATION_ENFORCEMENT:
    - OLD: CORTEX code never in user repos (blocked all writes)
    - NEW: CORTEX code writes to ACTIVE user repo (orchestrators create files)
    
    Features:
    - Automatic workspace detection
    - Operation-specific validation (read/write/delete/create)
    - CORTEX core protection (prevent self-modification)
    - Cross-workspace operation prevention
    - Detailed violation reporting
    
    Usage:
        validator = WorkspaceOperationValidator()
        
        # Validate file write
        result = validator.validate(
            target_path="/path/to/user/repo/src/feature.py",
            operation=OperationType.WRITE
        )
        
        if result == ValidationResult.DENIED:
            raise PermissionError("Cross-workspace write denied")
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize workspace operation validator.
        
        Args:
            cortex_root: Path to CORTEX installation (auto-detected if None)
        """
        self.cortex_root = cortex_root or self._find_cortex_root()
        self.active_workspace = detect_active_workspace()
        
        # Protected CORTEX core paths
        self.cortex_core_paths = [
            self.cortex_root / "src" / "tier0",
            self.cortex_root / "src" / "tier1",
            self.cortex_root / "src" / "tier2",
            self.cortex_root / "src" / "tier3",
            self.cortex_root / "src" / "cortex_agents",
            self.cortex_root / "src" / "orchestrators",
            self.cortex_root / "cortex-brain" / "tier0",
        ]
        
        logger.debug(
            f"WorkspaceOperationValidator initialized - "
            f"Active workspace: {self.active_workspace.name}"
        )
    
    def validate(
        self,
        target_path: Union[Path, str],
        operation: OperationType,
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate if operation is allowed on target path.
        
        Args:
            target_path: Path to file/directory for operation
            operation: Type of operation (READ, WRITE, DELETE, CREATE)
            context: Optional context dictionary
            
        Returns:
            ValidationResult (ALLOWED, DENIED, WARNING)
        """
        target_path = Path(target_path).resolve()
        context = context or {}
        
        # Check if target is within CORTEX core (protected)
        if self._is_cortex_core_path(target_path):
            if operation in [OperationType.WRITE, OperationType.DELETE, OperationType.CREATE]:
                logger.error(
                    f"❌ DENIED: Cannot {operation.value} CORTEX core path: {target_path}"
                )
                return ValidationResult.DENIED
        
        # Check if target is in active workspace
        in_active_workspace = self._is_in_active_workspace(target_path)
        
        # READ operations: Always allowed
        if operation == OperationType.READ:
            return ValidationResult.ALLOWED
        
        # WRITE/CREATE operations: Must be in active workspace
        if operation in [OperationType.WRITE, OperationType.CREATE]:
            if in_active_workspace:
                logger.debug(f"✅ ALLOWED: {operation.value} to active workspace")
                return ValidationResult.ALLOWED
            else:
                # Check if it's in CORTEX itself (allowed for self-operations)
                if self._is_in_cortex_root(target_path):
                    logger.debug(f"✅ ALLOWED: {operation.value} to CORTEX")
                    return ValidationResult.ALLOWED
                else:
                    logger.warning(
                        f"⚠️  WARNING: {operation.value} to non-active workspace: {target_path}"
                    )
                    return ValidationResult.WARNING
        
        # DELETE operations: Must be in active workspace or CORTEX
        if operation == OperationType.DELETE:
            if in_active_workspace or self._is_in_cortex_root(target_path):
                return ValidationResult.ALLOWED
            else:
                logger.error(
                    f"❌ DENIED: Cannot delete from non-active workspace: {target_path}"
                )
                return ValidationResult.DENIED
        
        # Default: Allow
        return ValidationResult.ALLOWED
    
    def validate_or_raise(
        self,
        target_path: Union[Path, str],
        operation: OperationType,
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Validate operation and raise exception if denied.
        
        Args:
            target_path: Path to file/directory for operation
            operation: Type of operation
            context: Optional context dictionary
            
        Raises:
            PermissionError: If operation is denied
        """
        result = self.validate(target_path, operation, context)
        
        if result == ValidationResult.DENIED:
            raise PermissionError(
                f"Workspace operation denied: {operation.value} on {target_path}\n"
                f"Active workspace: {self.active_workspace.name} ({self.active_workspace.path})\n"
                f"Target path not in active workspace"
            )
    
    def get_validation_report(
        self,
        target_path: Union[Path, str],
        operation: OperationType
    ) -> Dict[str, Any]:
        """
        Get detailed validation report.
        
        Args:
            target_path: Path to validate
            operation: Operation type
            
        Returns:
            Dictionary with validation details
        """
        target_path = Path(target_path).resolve()
        result = self.validate(target_path, operation)
        
        report = {
            'target_path': str(target_path),
            'operation': operation.value,
            'result': result.value,
            'active_workspace': {
                'id': self.active_workspace.workspace_id,
                'name': self.active_workspace.name,
                'path': str(self.active_workspace.path)
            },
            'checks': {
                'is_cortex_core': self._is_cortex_core_path(target_path),
                'in_active_workspace': self._is_in_active_workspace(target_path),
                'in_cortex_root': self._is_in_cortex_root(target_path)
            }
        }
        
        return report
    
    def _is_cortex_core_path(self, path: Path) -> bool:
        """Check if path is in CORTEX protected core."""
        path = path.resolve()
        for core_path in self.cortex_core_paths:
            core_path = core_path.resolve()
            try:
                path.relative_to(core_path)
                return True
            except ValueError:
                continue
        return False
    
    def _is_in_active_workspace(self, path: Path) -> bool:
        """Check if path is in active workspace."""
        try:
            path.relative_to(self.active_workspace.path)
            return True
        except ValueError:
            return False
    
    def _is_in_cortex_root(self, path: Path) -> bool:
        """Check if path is in CORTEX root."""
        try:
            path.relative_to(self.cortex_root)
            return True
        except ValueError:
            return False
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX installation root."""
        current = Path(__file__).parent
        
        while current != current.parent:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        raise RuntimeError("CORTEX installation not found")


# Global validator instance
_validator: Optional[WorkspaceOperationValidator] = None


def get_workspace_validator() -> WorkspaceOperationValidator:
    """
    Get global workspace operation validator instance.
    
    Usage:
        from src.tier0.workspace_operation_validator import get_workspace_validator
        
        validator = get_workspace_validator()
        validator.validate_or_raise("/path/to/file", OperationType.WRITE)
    """
    global _validator
    
    if _validator is None:
        _validator = WorkspaceOperationValidator()
    
    return _validator

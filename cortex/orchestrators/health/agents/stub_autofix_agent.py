"""Stub Auto-Fix Agent - Automatically Fix Stub Files

Detects stub files (redirect wrappers) and automatically fixes them by:
1. Deleting the stub file
2. Updating all imports to point directly to cortex.intelligence

Author: CORTEX Framework
Phase: PHASE-96
CORE Rules: CORE-008 (TDD), CORE-035 (Single Source of Truth)
"""

import ast
import re
from pathlib import Path
from typing import List, Tuple, Optional

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


class StubAutoFixAgent(BaseHealthAgent):
    """Agent for automatically fixing stub files.
    
    Detects redirect stubs (files that just re-export from deleted packages
    such as cortex.intelligence or cortex.lens) and fixes them by:
    - Deleting the stub file
    - Rewriting imports in other files to point to cortex.intelligence
    
    Attributes:
        name: Agent name
        description: Agent description
        config: Configuration with auto-fix settings
    """
    
    def __init__(self, config: dict = None) -> None:
        """Initialize Stub Auto-Fix Agent.
        
        Args:
            config: Optional configuration with:
                - auto_fix_enabled: Whether to auto-fix (default: False)
                - dry_run: Only report, don't fix (default: True)
                - backup_enabled: Create backups before fixing (default: True)
        """
        super().__init__(
            name="StubAutoFixAgent",
            description="Automatically fixes stub files and redirects imports",
            config=config,
        )
        
        self.auto_fix_enabled = self.config.get("auto_fix_enabled", False)
        self.dry_run = self.config.get("dry_run", True)
        self.backup_enabled = self.config.get("backup_enabled", True)
    
    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run stub detection and auto-fix.
        
        Args:
            workspace_root: Root path of workspace to check
        
        Returns:
            HealthCheckResult with fixed stubs
        """
        import time
        
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0
        
        # Find all Python files
        for py_file in workspace_root.rglob("*.py"):
            if self._should_exclude(py_file, workspace_root):
                continue
            
            files_scanned += 1
            
            # Check if file is a stub
            if self._is_redirect_stub(py_file):
                # Detect stub
                target_module = self._extract_target_module(py_file)
                
                issue = HealthIssue(
                    category=HealthIssueCategory.STUB,
                    severity=HealthIssueSeverity.HIGH,
                    file_path=py_file.relative_to(workspace_root),
                    description=f"Redirect stub → {target_module}",
                    line_number=1,
                    suggested_fix=f"Delete stub, update imports to {target_module}",
                )
                issues.append(issue)
                
                # Auto-fix if enabled
                if self.auto_fix_enabled and not self.dry_run:
                    self._fix_stub(py_file, target_module, workspace_root)
                    issue.description += " [FIXED]"
        
        duration = time.time() - start_time
        
        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "auto_fix_enabled": self.auto_fix_enabled,
                "dry_run": self.dry_run,
                "stubs_found": len(issues),
                "stubs_fixed": len(issues) if self.auto_fix_enabled and not self.dry_run else 0,
            },
        )
    
    def _should_exclude(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file should be excluded from scanning.
        
        Args:
            file_path: File to check
            workspace_root: Workspace root
        
        Returns:
            True if should exclude
        """
        import fnmatch
        
        exclude_patterns = [
            "*/_archives/*",
            "*/_workspaces/*",
            "*/.venv/*",
            "*/.git/*",
            "*/tests/*",
            "*/test_*.py",
            "*/__pycache__/*",
            "*/__init__.py",
        ]
        
        rel_path = str(file_path.relative_to(workspace_root))
        file_name = file_path.name
        
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(file_name, pattern.lstrip('*/')):
                return True
        
        return False
    
    def _is_redirect_stub(self, file_path: Path) -> bool:
        """Check if file is a redirect stub.
        
        A redirect stub is a file that:
        - Contains only imports from deleted packages (cortex.intelligence, cortex.lens)
        - Has < 10 lines of actual code
        - Has "REDIRECT" comment or re-export pattern
        
        Args:
            file_path: File to check
        
        Returns:
            True if file is a redirect stub
        """
        try:
            content = file_path.read_text()
            
            # Check for redirect markers
            if "REDIRECT" in content or "Re-export" in content:
                return True
            
            # Check if only imports from deleted packages (cortex.intelligence, cortex.lens)
            if "from cortex.intelligence" in content or "from cortex.lens" in content:
                lines = [
                    line for line in content.split('\n')
                    if line.strip() and not line.strip().startswith('#')
                ]
                
                # Very few lines + imports from deleted packages = likely stub
                if len(lines) <= 5:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def _extract_target_module(self, stub_file: Path) -> Optional[str]:
        """Extract the target module that stub redirects to.
        
        Args:
            stub_file: Stub file path
        
        Returns:
            Target module name (e.g., 'cortex.intelligence.domain.models')
        """
        try:
            content = stub_file.read_text()
            
            # Parse imports
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith("cortex.intelligence"):
                        return node.module
            
            return None
            
        except Exception:
            return None
    
    def _fix_stub(
        self,
        stub_file: Path,
        target_module: str,
        workspace_root: Path
    ) -> None:
        """Fix stub by deleting it and updating imports.
        
        Args:
            stub_file: Stub file to delete
            target_module: Target module to redirect imports to
            workspace_root: Workspace root
        """
        # Backup if enabled
        if self.backup_enabled:
            backup_path = stub_file.with_suffix('.py.backup')
            backup_path.write_text(stub_file.read_text())
        
        # Calculate stub module path
        stub_module = self._file_to_module(stub_file, workspace_root)
        
        # Update all imports in workspace
        self._update_imports(workspace_root, stub_module, target_module)
        
        # Delete stub file
        stub_file.unlink()
    
    def _file_to_module(self, file_path: Path, workspace_root: Path) -> str:
        """Convert file path to module name.
        
        Args:
            file_path: Python file path
            workspace_root: Workspace root
        
        Returns:
            Module name (e.g., 'cortex.domain.models')
        """
        rel_path = file_path.relative_to(workspace_root)
        module = str(rel_path.with_suffix('')).replace('/', '.')
        return module
    
    def _update_imports(
        self,
        workspace_root: Path,
        old_module: str,
        new_module: str
    ) -> None:
        """Update imports across workspace.
        
        Args:
            workspace_root: Workspace root
            old_module: Old module name to replace
            new_module: New module name
        """
        for py_file in workspace_root.rglob("*.py"):
            if self._should_exclude(py_file, workspace_root):
                continue
            
            try:
                content = py_file.read_text()
                
                # Replace import statements
                updated = content
                
                # Pattern 1: from old_module import X
                updated = re.sub(
                    rf'\bfrom {re.escape(old_module)} import\b',
                    f'from {new_module} import',
                    updated
                )
                
                # Pattern 2: import old_module
                updated = re.sub(
                    rf'\bimport {re.escape(old_module)}\b',
                    f'import {new_module}',
                    updated
                )
                
                # Write back if changed
                if updated != content:
                    py_file.write_text(updated)
                    
            except Exception:
                # Skip files with errors
                continue


__all__ = ["StubAutoFixAgent"]

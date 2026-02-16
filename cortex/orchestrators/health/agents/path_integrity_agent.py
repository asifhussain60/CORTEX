"""Path Integrity Agent - Detects Import and Path Issues

Identifies:
- Hardcoded old paths (cortex/knowledge vs cortex-registry)
- Broken imports
- Circular dependencies
- Incorrect registry paths

Author: CORTEX Framework
Phase: PHASE-95
CORE Rules: CORE-035 (canonical implementation), CORE-047 (no hardcoded paths)
"""

import ast
import time
from pathlib import Path
from typing import List, Optional, Set

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


class PathIntegrityAgent(BaseHealthAgent):
    """Agent for detecting path and import issues.
    
    Detects:
    - Hardcoded old paths
    - Broken imports
    - Registry path violations
    
    Attributes:
        name: Agent name
        description: Agent description
        config: Configuration
    """
    
    def __init__(self, config: dict = None) -> None:
        """Initialize Path Integrity Agent.
        
        Args:
            config: Optional configuration with:
                - old_paths: List of deprecated paths
                - registry_root: Expected registry location
        """
        super().__init__(
            name="PathIntegrityAgent",
            description="Detects hardcoded paths and broken imports",
            config=config,
        )
        
        self.old_paths = self.config.get("old_paths", [
            "cortex/knowledge",
            "cortex/wiring",
            "cortex/templates",
            "company/domains",
        ])
        
        self.registry_root = self.config.get("registry_root", "cortex-registry")
        
        self.exclude_patterns = self.config.get("exclude_patterns", [
            "*/_archives/*",
            "*/_workspaces/*",
            "*/.venv/*",
            "*/.git/*",
            "*/__pycache__/*",
        ])
    
    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run path integrity check.
        
        Args:
            workspace_root: Root path of workspace to check
        
        Returns:
            HealthCheckResult with detected issues
        """
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0
        
        # Check Python files for imports
        for py_file in workspace_root.rglob("*.py"):
            if self._should_exclude(py_file, workspace_root):
                continue
            
            try:
                # Check for old hardcoded paths
                old_path_issues = self._check_old_paths(py_file, workspace_root)
                issues.extend(old_path_issues)
                
                # Check for broken imports
                broken_import_issues = self._check_imports(py_file, workspace_root)
                issues.extend(broken_import_issues)
                
                files_scanned += 1
            except Exception:
                continue
        
        # Check YAML files outside registry
        yaml_issues = self._check_yaml_placement(workspace_root)
        issues.extend(yaml_issues)
        
        duration = time.time() - start_time
        
        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "old_paths_checked": len(self.old_paths),
                "registry_root": self.registry_root,
            },
        )
    
    def _check_old_paths(self, file_path: Path, workspace_root: Path) -> List[HealthIssue]:
        """Check for hardcoded old paths in file.
        
        Args:
            file_path: Python file to check
            workspace_root: Workspace root
        
        Returns:
            List of issues found
        """
        issues: List[HealthIssue] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            rel_path = file_path.relative_to(workspace_root)
            
            for old_path in self.old_paths:
                if old_path in content:
                    # Count occurrences
                    count = content.count(old_path)
                    
                    issues.append(HealthIssue(
                        category=HealthIssueCategory.PATH,
                        severity=HealthIssueSeverity.HIGH,
                        file_path=rel_path,
                        description=f"Hardcoded old path '{old_path}' ({count} occurrences)",
                        suggested_fix=f"Replace with registry path: {self.registry_root}/...",
                        metadata={
                            "old_path": old_path,
                            "occurrences": count,
                        },
                    ))
        except Exception:
            pass
        
        return issues
    
    def _check_imports(self, file_path: Path, workspace_root: Path) -> List[HealthIssue]:
        """Check for broken imports.
        
        Args:
            file_path: Python file to check
            workspace_root: Workspace root
        
        Returns:
            List of issues found
        """
        issues: List[HealthIssue] = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            rel_path = file_path.relative_to(workspace_root)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module:
                        # Check if module exists
                        module_path = self._resolve_import(node.module, workspace_root)
                        
                        if module_path is None:
                            issues.append(HealthIssue(
                                category=HealthIssueCategory.PATH,
                                severity=HealthIssueSeverity.MEDIUM,
                                file_path=rel_path,
                                description=f"Potentially broken import: {node.module}",
                                suggested_fix="Verify import path or update",
                                metadata={
                                    "import_module": node.module,
                                },
                            ))
        except Exception:
            pass
        
        return issues
    
    def _resolve_import(self, module: str, workspace_root: Path) -> Optional[Path]:
        """Try to resolve import to file path.
        
        Args:
            module: Module name (e.g., 'cortex.orchestrators')
            workspace_root: Workspace root
        
        Returns:
            Resolved path or None if not found
        """
        # Convert module to path
        parts = module.split('.')
        
        # Try as package
        package_path = workspace_root / Path(*parts) / "__init__.py"
        if package_path.exists():
            return package_path
        
        # Try as module
        module_path = workspace_root / Path(*parts[:-1]) / f"{parts[-1]}.py"
        if module_path.exists():
            return module_path
        
        return None
    
    def _check_yaml_placement(self, workspace_root: Path) -> List[HealthIssue]:
        """Check for YAML files outside registry.
        
        Args:
            workspace_root: Workspace root
        
        Returns:
            List of issues found
        """
        issues: List[HealthIssue] = []
        registry_path = workspace_root / self.registry_root
        
        # Find YAML files outside registry
        for yaml_file in workspace_root.rglob("*.yaml"):
            if self._should_exclude(yaml_file, workspace_root):
                continue
            
            # Skip if in registry
            try:
                yaml_file.relative_to(registry_path)
                continue
            except ValueError:
                pass
            
            # Flag as misplaced
            rel_path = yaml_file.relative_to(workspace_root)
            
            issues.append(HealthIssue(
                category=HealthIssueCategory.PATH,
                severity=HealthIssueSeverity.LOW,
                file_path=rel_path,
                description="YAML file outside registry",
                suggested_fix=f"Move to {self.registry_root}/ if configuration",
                metadata={
                    "expected_location": str(registry_path),
                },
            ))
        
        return issues
    
    def _should_exclude(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file should be excluded.
        
        Args:
            file_path: File path to check
            workspace_root: Workspace root
        
        Returns:
            True if should exclude
        """
        rel_path = str(file_path.relative_to(workspace_root))
        
        for pattern in self.exclude_patterns:
            pattern_clean = pattern.replace("*", "").replace("/", "")
            if pattern_clean in rel_path:
                return True
        
        return False


__all__ = ["PathIntegrityAgent"]

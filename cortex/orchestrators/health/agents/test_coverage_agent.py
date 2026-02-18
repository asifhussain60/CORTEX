"""Test Coverage Agent - Detects Missing Tests

Identifies:
- Python files without corresponding test files
- Low test coverage areas
- Untested modules

Author: CORTEX Framework
Phase: PHASE-95
CORE Rules: CORE-008 (TDD), CORE-001 (incremental delivery)
"""

import time
from pathlib import Path
from typing import List, Set

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


class TestCoverageAgent(BaseHealthAgent):
    """Agent for detecting missing test coverage.
    
    Detects:
    - Python files without test files
    - Modules without any tests
    - Test files without corresponding source
    
    Attributes:
        name: Agent name
        description: Agent description
        config: Configuration
    """
    
    def __init__(self, config: dict = None) -> None:
        """Initialize Test Coverage Agent.
        
        Args:
            config: Optional configuration with:
                - test_dirs: Directories to search for tests
                - exclude_patterns: Patterns to exclude
        """
        super().__init__(
            name="TestCoverageAgent",
            description="Detects missing test coverage",
            config=config,
        )
        
        self.test_dirs = self.config.get("test_dirs", ["tests", "test"])
        
        self.exclude_patterns = self.config.get("exclude_patterns", [
            "*/_archives/*",
            "*/_workspaces/*",
            "*/.venv/*",
            "*/.git/*",
            "*/__pycache__/*",
            "*/tests/*",  # Don't check test files themselves
            "*/__init__.py",  # Init files often don't need tests
        ])
    
    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run test coverage check.
        
        Args:
            workspace_root: Root path of workspace to check
        
        Returns:
            HealthCheckResult with detected issues
        """
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0
        
        # Find all test files
        test_files = self._find_test_files(workspace_root)
        
        # Check each Python file for corresponding tests
        for py_file in workspace_root.rglob("*.py"):
            if self._should_exclude(py_file, workspace_root):
                continue
            
            try:
                has_test = self._has_test_file(py_file, test_files, workspace_root)
                
                if not has_test:
                    rel_path = py_file.relative_to(workspace_root)
                    
                    # Determine severity based on file location
                    if "core" in str(rel_path) or "orchestrators" in str(rel_path):
                        severity = HealthIssueSeverity.HIGH
                    elif "utils" in str(rel_path) or "helpers" in str(rel_path):
                        severity = HealthIssueSeverity.MEDIUM
                    else:
                        severity = HealthIssueSeverity.LOW
                    
                    issues.append(HealthIssue(
                        category=HealthIssueCategory.MISSING_TEST,
                        severity=severity,
                        file_path=rel_path,
                        description="No corresponding test file found",
                        suggested_fix=f"Create test file in tests/ directory",
                        metadata={
                            "expected_test_paths": self._get_expected_test_paths(py_file, workspace_root),
                        },
                    ))
                
                files_scanned += 1
            except Exception:
                continue
        
        duration = time.time() - start_time
        
        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "test_files_found": len(test_files),
                "test_dirs": self.test_dirs,
            },
        )
    
    def _find_test_files(self, workspace_root: Path) -> Set[Path]:
        """Find all test files in workspace.
        
        Args:
            workspace_root: Workspace root
        
        Returns:
            Set of test file paths
        """
        test_files: Set[Path] = set()
        
        # Search in configured test directories
        for test_dir in self.test_dirs:
            test_path = workspace_root / test_dir
            if test_path.exists():
                for test_file in test_path.rglob("test_*.py"):
                    test_files.add(test_file)
        
        # Also search for co-located test files
        for test_file in workspace_root.rglob("test_*.py"):
            if not self._should_exclude(test_file, workspace_root):
                test_files.add(test_file)
        
        return test_files
    
    def _has_test_file(self, py_file: Path, test_files: Set[Path], workspace_root: Path) -> bool:
        """Check if Python file has corresponding test.
        
        Args:
            py_file: Python file to check
            test_files: Set of all test files
            workspace_root: Workspace root
        
        Returns:
            True if test file exists
        """
        filename = py_file.stem
        expected_test_name = f"test_{filename}.py"
        
        # Check if any test file matches
        for test_file in test_files:
            if test_file.name == expected_test_name:
                return True
        
        return False
    
    def _get_expected_test_paths(self, py_file: Path, workspace_root: Path) -> List[str]:
        """Get list of expected test file paths.
        
        Args:
            py_file: Python file
            workspace_root: Workspace root
        
        Returns:
            List of possible test paths
        """
        rel_path = py_file.relative_to(workspace_root)
        filename = py_file.stem
        
        expected_paths = []
        
        # Pattern 1: tests/unit/module/test_file.py
        expected_paths.append(f"tests/unit/{rel_path.parent}/test_{filename}.py")
        
        # Pattern 2: tests/module/test_file.py
        expected_paths.append(f"tests/{rel_path.parent}/test_{filename}.py")
        
        # Pattern 3: Co-located test_file.py
        expected_paths.append(str(py_file.parent / f"test_{filename}.py"))
        
        return expected_paths
    
    def _should_exclude(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file should be excluded.
        
        Args:
            file_path: File path to check
            workspace_root: Workspace root
        
        Returns:
            True if should exclude
        """
        rel_path = file_path.relative_to(workspace_root)
        parts = set(rel_path.parts)
        
        for pattern in self.exclude_patterns:
            stripped = pattern.strip("*/")
            if stripped and stripped in parts:
                return True
        
        return False


__all__ = ["TestCoverageAgent"]

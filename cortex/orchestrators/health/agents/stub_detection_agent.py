"""Weak Implementation Detection Agent

Identifies files that are stubs disguising as implementations:
- < 200 LOC (configurable)
- Low McCabe complexity (< 5)
- Only imports/re-exports
- Missing docstrings
- No corresponding tests

Author: CORTEX Framework
Phase: PHASE-95
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import ast
import time
from pathlib import Path
from typing import List

try:
    from radon.complexity import cc_visit
except ImportError:
    cc_visit = None

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


class StubDetectionAgent(BaseHealthAgent):
    """Agent for detecting stub files and weak implementations.
    
    Detects:
    - Files < 200 LOC with low complexity
    - Files that only import/re-export
    - Files missing docstrings
    - Files without corresponding tests
    
    Attributes:
        name: Agent name
        description: Agent description
        config: Configuration with thresholds
    """
    
    def __init__(self, config: dict = None) -> None:
        """Initialize Stub Detection Agent.
        
        Args:
            config: Optional configuration with:
                - loc_threshold: Max LOC for stub (default: 200)
                - complexity_threshold: Max complexity (default: 5)
                - exclude_patterns: Patterns to exclude
        """
        super().__init__(
            name="StubDetectionAgent",
            description="Detects weak implementations and stub files",
            config=config,
        )
        
        self.loc_threshold = self.config.get("loc_threshold", 200)
        self.complexity_threshold = self.config.get("complexity_threshold", 5)
        self.exclude_patterns = self.config.get("exclude_patterns", [
            "*/_archives/*",
            "*/_workspaces/*",
            "*/.venv/*",
            "*/.git/*",
            "*/tests/*",
            "*/test_*.py",  # Test files (anywhere)
            "*/__pycache__/*",
            "*/__init__.py",  # Init files are often small
            "*/conftest.py",  # Test configuration files
            "*/models.py",  # Data models (legitimately simple)
            "*/bootstrap.py",  # Bootstrap files
            "*/*_metrics.py",  # Metrics collectors (simple by design)
        ])
    
    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run stub detection check.
        
        Args:
            workspace_root: Root path of workspace to check
        
        Returns:
            HealthCheckResult with detected stubs
        """
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0
        
        # Find all Python files
        for py_file in workspace_root.rglob("*.py"):
            if self._should_exclude(py_file, workspace_root):
                continue
            
            try:
                loc = self._calculate_loc(py_file)
                
                # Only check files under LOC threshold
                if loc < self.loc_threshold:
                    complexity = self._calculate_complexity(py_file)
                    has_docstring = self._has_docstring(py_file)
                    has_tests = self._has_tests(py_file, workspace_root)
                    is_stub = self._is_stub_pattern(py_file)
                    
                    # Flag as stub if multiple indicators
                    stub_indicators = 0
                    if complexity < self.complexity_threshold:
                        stub_indicators += 1
                    if not has_docstring:
                        stub_indicators += 1
                    if not has_tests:
                        stub_indicators += 1
                    if is_stub:
                        stub_indicators += 2  # Strong indicator
                    
                    # Require 3+ indicators to flag as issue (reduced false positives)
                    # Files can have low complexity legitimately (models, configs, etc.)
                    if stub_indicators >= 3:
                        rel_path = py_file.relative_to(workspace_root)
                        
                        # Determine severity
                        if stub_indicators >= 4:
                            severity = HealthIssueSeverity.HIGH
                        else:
                            severity = HealthIssueSeverity.MEDIUM
                        
                        issues.append(HealthIssue(
                            category=HealthIssueCategory.STUB,
                            severity=severity,
                            file_path=rel_path,
                            description=f"Weak implementation ({loc} LOC, complexity {complexity:.1f})",
                            suggested_fix="Enhance implementation or delete if truly a stub",
                            metadata={
                                "loc": loc,
                                "complexity": complexity,
                                "has_docstring": has_docstring,
                                "has_tests": has_tests,
                                "is_stub_pattern": is_stub,
                                "stub_indicators": stub_indicators,
                            },
                        ))
                
                files_scanned += 1
            except Exception:
                # Skip files that can't be analyzed
                continue
        
        duration = time.time() - start_time
        
        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "loc_threshold": self.loc_threshold,
                "complexity_threshold": self.complexity_threshold,
            },
        )
    
    def _calculate_loc(self, file_path: Path) -> int:
        """Calculate lines of code (non-blank, non-comment).
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Number of code lines
        """
        loc = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            in_multiline_string = False
            for line in f:
                stripped = line.strip()
                
                # Toggle multiline string state
                if '"""' in stripped or "'''" in stripped:
                    in_multiline_string = not in_multiline_string
                    continue
                
                # Skip blank lines and comments
                if not stripped or stripped.startswith('#') or in_multiline_string:
                    continue
                
                loc += 1
        
        return loc
    
    def _calculate_complexity(self, file_path: Path) -> float:
        """Calculate McCabe complexity using radon.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Average complexity score
        """
        if cc_visit is None:
            return 0.0
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            complexity_results = cc_visit(code)
            
            if not complexity_results:
                return 0.0
            
            # Calculate average complexity
            total_complexity = sum(result.complexity for result in complexity_results)
            return total_complexity / len(complexity_results)
        except Exception:
            return 0.0
    
    def _has_docstring(self, file_path: Path) -> bool:
        """Check if file has module docstring.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            True if module docstring exists
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            return ast.get_docstring(tree) is not None
        except Exception:
            return False
    
    def _has_tests(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if corresponding test file exists.
        
        Args:
            file_path: Path to Python file
            workspace_root: Workspace root
        
        Returns:
            True if test file found
        """
        # Try multiple test file patterns
        rel_path = file_path.relative_to(workspace_root)
        
        test_patterns = [
            workspace_root / "tests" / "unit" / rel_path.parent / f"test_{rel_path.name}",
            workspace_root / "tests" / rel_path.parent / f"test_{rel_path.name}",
            file_path.parent / f"test_{file_path.name}",
        ]
        
        return any(pattern.exists() for pattern in test_patterns)
    
    def _is_stub_pattern(self, file_path: Path) -> bool:
        """Check if file follows stub pattern (only imports/exports).
        
        Args:
            file_path: Path to Python file
        
        Returns:
            True if file is likely a stub
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            tree = ast.parse(code)
            
            # Count different node types
            imports = 0
            functions = 0
            classes = 0
            assignments = 0
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports += 1
                elif isinstance(node, ast.FunctionDef):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                elif isinstance(node, ast.Assign):
                    assignments += 1
            
            # Stub if mostly imports with minimal logic
            return imports > 0 and (functions + classes) <= 1 and assignments <= 2
        except Exception:
            return False
    
    def _should_exclude(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file should be excluded.
        
        Args:
            file_path: File path to check
            workspace_root: Workspace root
        
        Returns:
            True if should exclude
        """
        import fnmatch
        
        rel_path = str(file_path.relative_to(workspace_root))
        file_name = file_path.name
        
        for pattern in self.exclude_patterns:
            # Check both full path and filename
            if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(file_name, pattern.lstrip('*/')):
                return True
        
        return False


__all__ = ["StubDetectionAgent"]

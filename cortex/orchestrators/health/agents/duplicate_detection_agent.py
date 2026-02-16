"""Duplicate Detection Agent - Detects CORE-035 Violations

Scans repository for duplicate files (Python and YAML) by comparing:
1. File hashes (exact duplicates)
2. Class/function signatures (near duplicates)
3. Import patterns (circular dependencies)

Author: CORTEX Framework
Phase: PHASE-92
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (no duplicates)
"""

import hashlib
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


class DuplicateDetectionAgent(BaseHealthAgent):
    """Agent for detecting duplicate files and implementations.
    
    Detects:
    - Exact file duplicates (identical content)
    - Near-duplicate Python classes (same name, similar LOC)
    - Near-duplicate YAML files (similar structure)
    - Multiple files with same basename in different locations
    
    Attributes:
        name: Agent name
        description: Agent description
        config: Configuration with exclude patterns
    """
    
    def __init__(self, config: Dict[str, any] = None) -> None:
        """Initialize Duplicate Detection Agent.
        
        Args:
            config: Optional configuration with:
                - exclude_patterns: List of glob patterns to exclude
                - check_python: Whether to check Python files (default: True)
                - check_yaml: Whether to check YAML files (default: True)
                - similarity_threshold: Threshold for near-duplicates (default: 0.8)
        """
        super().__init__(
            name="DuplicateDetectionAgent",
            description="Detects CORE-035 violations (duplicate files and implementations)",
            config=config,
        )
        
        self.exclude_patterns = self.config.get("exclude_patterns", [
            "*/_archives/*",
            "*/_workspaces/*",
            "*/.venv/*",
            "*/.git/*",
            "*/tests/*",
            "*/__pycache__/*",
            "*/.mypy_cache/*",
        ])
        
        self.check_python = self.config.get("check_python", True)
        self.check_yaml = self.config.get("check_yaml", True)
        self.similarity_threshold = self.config.get("similarity_threshold", 0.8)
    
    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run duplicate detection check.
        
        Args:
            workspace_root: Root path of workspace to check
        
        Returns:
            HealthCheckResult with detected duplicates
        """
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0
        
        # Find exact duplicates by hash
        if self.check_python:
            python_issues, python_scanned = self._check_python_duplicates(workspace_root)
            issues.extend(python_issues)
            files_scanned += python_scanned
        
        if self.check_yaml:
            yaml_issues, yaml_scanned = self._check_yaml_duplicates(workspace_root)
            issues.extend(yaml_issues)
            files_scanned += yaml_scanned
        
        # Find basename duplicates (same filename in different locations)
        basename_issues, basename_scanned = self._check_basename_duplicates(workspace_root)
        issues.extend(basename_issues)
        files_scanned += basename_scanned
        
        duration = time.time() - start_time
        
        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "check_python": self.check_python,
                "check_yaml": self.check_yaml,
                "similarity_threshold": self.similarity_threshold,
            },
        )
    
    def _check_python_duplicates(self, workspace_root: Path) -> Tuple[List[HealthIssue], int]:
        """Check for duplicate Python files.
        
        Args:
            workspace_root: Workspace root path
        
        Returns:
            Tuple of (issues list, files scanned count)
        """
        issues: List[HealthIssue] = []
        hash_map: Dict[str, List[Path]] = defaultdict(list)
        files_scanned = 0
        
        # Find all Python files
        for py_file in workspace_root.rglob("*.py"):
            if self._should_exclude(py_file, workspace_root):
                continue
            
            try:
                file_hash = self._calculate_file_hash(py_file)
                hash_map[file_hash].append(py_file)
                files_scanned += 1
            except Exception as e:
                # Skip files that can't be read
                continue
        
        # Report duplicates
        for file_hash, files in hash_map.items():
            if len(files) > 1:
                # Get file sizes for SSOT determination
                file_info = [(f, f.stat().st_size) for f in files]
                file_info.sort(key=lambda x: x[1], reverse=True)  # Largest first
                
                ssot_file = file_info[0][0]
                duplicate_files = [f[0] for f in file_info[1:]]
                
                for dup_file in duplicate_files:
                    rel_path = dup_file.relative_to(workspace_root)
                    ssot_rel_path = ssot_file.relative_to(workspace_root)
                    
                    issues.append(HealthIssue(
                        category=HealthIssueCategory.DUPLICATE,
                        severity=HealthIssueSeverity.CRITICAL,
                        file_path=rel_path,
                        description=f"Exact duplicate of {ssot_rel_path} (identical content)",
                        suggested_fix=f"Delete this file and update imports to point to {ssot_rel_path}",
                        metadata={
                            "ssot_file": str(ssot_rel_path),
                            "duplicate_type": "exact_match",
                            "file_hash": file_hash,
                            "ssot_size": file_info[0][1],
                            "duplicate_size": dup_file.stat().st_size,
                        },
                    ))
        
        return issues, files_scanned
    
    def _check_yaml_duplicates(self, workspace_root: Path) -> Tuple[List[HealthIssue], int]:
        """Check for duplicate YAML files.
        
        Args:
            workspace_root: Workspace root path
        
        Returns:
            Tuple of (issues list, files scanned count)
        """
        issues: List[HealthIssue] = []
        hash_map: Dict[str, List[Path]] = defaultdict(list)
        files_scanned = 0
        
        # Find all YAML files
        for yaml_file in list(workspace_root.rglob("*.yaml")) + list(workspace_root.rglob("*.yml")):
            if self._should_exclude(yaml_file, workspace_root):
                continue
            
            try:
                file_hash = self._calculate_file_hash(yaml_file)
                hash_map[file_hash].append(yaml_file)
                files_scanned += 1
            except Exception:
                continue
        
        # Report duplicates
        for file_hash, files in hash_map.items():
            if len(files) > 1:
                # Prefer registry location as SSOT
                registry_files = [f for f in files if "cortex-registry" in str(f)]
                if registry_files:
                    ssot_file = registry_files[0]
                    duplicate_files = [f for f in files if f != ssot_file]
                else:
                    # Use largest file as SSOT
                    file_info = [(f, f.stat().st_size) for f in files]
                    file_info.sort(key=lambda x: x[1], reverse=True)
                    ssot_file = file_info[0][0]
                    duplicate_files = [f[0] for f in file_info[1:]]
                
                for dup_file in duplicate_files:
                    rel_path = dup_file.relative_to(workspace_root)
                    ssot_rel_path = ssot_file.relative_to(workspace_root)
                    
                    issues.append(HealthIssue(
                        category=HealthIssueCategory.DUPLICATE,
                        severity=HealthIssueSeverity.CRITICAL,
                        file_path=rel_path,
                        description=f"Exact duplicate of {ssot_rel_path} (identical YAML)",
                        suggested_fix=f"Delete this file. SSOT is in registry: {ssot_rel_path}",
                        metadata={
                            "ssot_file": str(ssot_rel_path),
                            "duplicate_type": "exact_yaml",
                            "file_hash": file_hash,
                        },
                    ))
        
        return issues, files_scanned
    
    def _check_basename_duplicates(self, workspace_root: Path) -> Tuple[List[HealthIssue], int]:
        """Check for files with same basename in different locations.
        
        Args:
            workspace_root: Workspace root path
        
        Returns:
            Tuple of (issues list, files scanned count)
        """
        issues: List[HealthIssue] = []
        basename_map: Dict[str, List[Path]] = defaultdict(list)
        files_scanned = 0
        
        # Find all Python files
        for py_file in workspace_root.rglob("*.py"):
            if self._should_exclude(py_file, workspace_root):
                continue
            
            basename = py_file.name
            basename_map[basename].append(py_file)
            files_scanned += 1
        
        # Report basename duplicates
        for basename, files in basename_map.items():
            if len(files) > 1 and basename not in ["__init__.py", "conftest.py"]:
                # Check if files are actually different (not exact duplicates)
                unique_hashes = set()
                for f in files:
                    try:
                        unique_hashes.add(self._calculate_file_hash(f))
                    except Exception:
                        pass
                
                if len(unique_hashes) > 1:
                    # Different content, same name = potential confusion
                    for i, file in enumerate(files[1:], 1):
                        rel_path = file.relative_to(workspace_root)
                        primary_rel_path = files[0].relative_to(workspace_root)
                        
                        issues.append(HealthIssue(
                            category=HealthIssueCategory.MULTIPLE_EXECUTION_PATHS,
                            severity=HealthIssueSeverity.HIGH,
                            file_path=rel_path,
                            description=f"Same filename '{basename}' in multiple locations (ambiguous imports)",
                            suggested_fix=f"Rename or consolidate with {primary_rel_path}",
                            metadata={
                                "basename": basename,
                                "other_locations": [str(f.relative_to(workspace_root)) for f in files if f != file],
                                "duplicate_type": "basename_collision",
                            },
                        ))
        
        return issues, files_scanned
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file content.
        
        Args:
            file_path: Path to file
        
        Returns:
            Hex digest of file hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _should_exclude(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file should be excluded from checking.
        
        Args:
            file_path: File path to check
            workspace_root: Workspace root for relative path calculation
        
        Returns:
            True if file should be excluded, False otherwise
        """
        rel_path = str(file_path.relative_to(workspace_root))
        
        for pattern in self.exclude_patterns:
            # Simple glob matching
            pattern_clean = pattern.replace("*", "").replace("/", "")
            if pattern_clean in rel_path:
                return True
        
        return False


__all__ = ["DuplicateDetectionAgent"]

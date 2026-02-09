# AC_START: AC-PHASE38.0-IMPL-002
# Stage 11: ScreamingCaseDetector - Identify SCREAMING_CASE files for migration
# Author: CORTEX Architect | Date: 2026-02-09
# Description: Detects files with SCREAMING_CASE naming and plans kebab-case migration

from typing import List, Dict, Set, Optional
from pathlib import Path
from dataclasses import dataclass
import re


@dataclass
class ScreamingCaseFile:
    """Represents a file with SCREAMING_CASE naming."""
    file_path: Path
    current_name: str
    proposed_name: str
    references: List[str]
    directories_using: Set[str]


class ScreamingCaseDetector:
    """
    Detects files and directories using SCREAMING_CASE naming convention.
    
    CORTEX Standard: kebab-case for files (orchestrator-name.py)
    CORTEX Standard: SCREAMING_CASE ONLY for constants (MAX_RETRY_COUNT)
    
    This detector helps migrate codebase to proper naming standards.
    
    Responsibilities:
    - Identify files with SCREAMING_CASE names
    - Identify directories with SCREAMING_CASE names  
    - Find all references to these files/dirs
    - Generate migration plans
    """
    
    def __init__(self, workspace_root: Path):
        """Initialize detector with workspace root."""
        self.workspace_root = Path(workspace_root)
        self.screaming_pattern = re.compile(r'^[A-Z][A-Z0-9_]*$')
        
    def detect_screaming_case_files(self) -> List[ScreamingCaseFile]:
        """Scan for Python files using SCREAMING_CASE naming."""
        violations = []
        
        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_skip(py_file):
                continue
            
            file_stem = py_file.stem
            
            # Check if filename is SCREAMING_CASE
            if self._is_screaming_case(file_stem):
                proposed_name = self._convert_to_kebab_case(file_stem)
                references = self._find_file_references(py_file)
                dirs_using = self._find_directory_references(file_stem)
                
                violations.append(ScreamingCaseFile(
                    file_path=py_file,
                    current_name=file_stem,
                    proposed_name=proposed_name,
                    references=references,
                    directories_using=dirs_using
                ))
        
        return violations
    
    def detect_screaming_case_directories(self) -> Dict[Path, str]:
        """Scan for directories using SCREAMING_CASE naming."""
        violations = {}
        
        for directory in self.workspace_root.rglob("*"):
            if not directory.is_dir() or self._should_skip_dir(directory):
                continue
            
            dir_name = directory.name
            
            if self._is_screaming_case(dir_name):
                proposed_name = self._convert_to_kebab_case(dir_name)
                violations[directory] = proposed_name
        
        return violations
    
    def _is_screaming_case(self, name: str) -> bool:
        """Check if name is SCREAMING_CASE."""
        # Must start with uppercase letter
        if not name or not name[0].isupper():
            return False
        
        # Must not contain underscores to be valid (SCREAMING_CASE has underscores, we want to catch it)
        if "_" not in name:
            return False
        
        # Check if it matches the pattern (all caps with underscores)
        return bool(self.screaming_pattern.match(name))
    
    def _convert_to_kebab_case(self, name: str) -> str:
        """Convert SCREAMING_CASE to kebab-case."""
        return name.lower().replace("_", "-")
    
    def _find_file_references(self, file_path: Path) -> List[str]:
        """Find all references to a file."""
        references = []
        file_stem = file_path.stem
        
        # Patterns to search for
        patterns = [
            f"from {file_stem} import",
            f"import {file_stem}",
            f"'{file_stem}'",
            f'"{file_stem}"',
            f"from .{file_stem}",
            f"from ..{file_stem}",
        ]
        
        for py_file in self.workspace_root.rglob("*.py"):
            if py_file == file_path or self._should_skip(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for pattern in patterns:
                    if pattern in content:
                        references.append(str(py_file))
                        break
            except Exception:
                pass
        
        return references
    
    def _find_directory_references(self, dir_name: str) -> Set[str]:
        """Find files that reference a directory."""
        using_dirs = set()
        
        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_skip(py_file):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                
                # Check for directory references in imports
                if f"from {dir_name}" in content or f"import {dir_name}" in content:
                    using_dirs.add(str(py_file))
                
                # Check for path-based references
                if f"/{dir_name}/" in content or f"\"{dir_name}\"" in content:
                    using_dirs.add(str(py_file))
            except Exception:
                pass
        
        return using_dirs
    
    def generate_migration_plan(self, violations: List[ScreamingCaseFile]) -> Dict:
        """Generate comprehensive migration plan."""
        return {
            "total_violations": len(violations),
            "files_to_rename": violations,
            "total_references": sum(len(v.references) for v in violations),
            "priority": "high" if len(violations) > 5 else "medium",
            "estimated_effort": f"{len(violations) * 15} minutes",
            "automation_feasible": all(
                len(v.references) < 100 for v in violations
            )
        }
    
    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [".venv", "__pycache__", ".git", "node_modules", ".egg-info", ".pytest_cache"]
        return any(pattern in file_path.parts for pattern in skip_patterns)
    
    def _should_skip_dir(self, dir_path: Path) -> bool:
        """Check if directory should be skipped."""
        skip_dirs = {".venv", "__pycache__", ".git", "node_modules", ".egg-info", ".pytest_cache"}
        return dir_path.name in skip_dirs


# AC_COMPLETE: AC-PHASE38.0-IMPL-002 ✅

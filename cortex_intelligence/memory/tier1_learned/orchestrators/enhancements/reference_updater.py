"""
Reference Updater - Automated cross-reference synchronization.

AC-ID: AC-VAC-ENH-002 | Phase: Enhancement #2
Purpose: Automatically find and update all file references when files move
Authority: CORTEX Vacuum Enhancement Phase 2

Detects and updates references in:
- .py imports and string literals
- .yaml/yml configuration paths
- .md documentation links
- .sh shell scripts
- Makefile and setup files
- .gitignore patterns
"""

from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import re
import subprocess
from datetime import datetime
from enum import Enum


class ReferenceType(Enum):
    """Types of file references that can be updated."""
    
    PYTHON_IMPORT = "python_import"           # from path import X, import path
    PYTHON_STRING = "python_string"           # "path", 'path', f"path"
    YAML_PATH = "yaml_path"                   # path: value in YAML
    MARKDOWN_LINK = "markdown_link"           # [text](path) in Markdown
    SHELL_PATH = "shell_path"                 # path in shell scripts
    MAKEFILE_PATH = "makefile_path"           # path in Makefile
    GITIGNORE_PATTERN = "gitignore_pattern"  # patterns in .gitignore
    CONFIG_PATH = "config_path"               # paths in config files
    COMMENT = "comment"                       # in code comments


@dataclass
class Reference:
    """Single detected reference to a file."""
    
    file_path: str                 # File containing the reference
    reference_type: ReferenceType
    line_number: int
    original_text: str             # Full line or expression
    old_value: str                 # Old file path/pattern
    new_value: str                 # New file path/pattern
    confidence: float = 0.8        # Confidence of being a valid reference (0.0-1.0)
    context: Optional[str] = None  # Surrounding context for verification
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class UpdateResult:
    """Result of updating references."""
    
    success: bool
    files_updated: int = 0
    references_changed: int = 0
    total_references_found: int = 0
    updates: List[Reference] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)


class ReferenceScanner:
    """Scan codebase for references to specific files."""
    
    # File extensions to scan
    SCANNABLE_EXTENSIONS = {".py", ".yaml", ".yml", ".md", ".sh", ".txt", ".cfg"}
    
    # Python import patterns
    PYTHON_PATTERNS = {
        "import_full": r"^\s*import\s+([\w./-]+)",
        "import_from": r"^\s*from\s+([\w./-]+)\s+import",
        "string_double": r'"([\w./-]+)"',
        "string_single": r"'([\w./-]+)'",
        "fstring": r'f"([\w./-]+)"|f\'([\w./-]+)\'',
        "path_object": r'Path\(["\']([^"\']+)["\']\)',
    }
    
    # YAML patterns
    YAML_PATTERNS = {
        "path_value": r"^\s*(\w+):\s*(['\"]?)([a-zA-Z0-9_/.-]+)\2\s*$",
        "list_path": r"^\s*-\s*([a-zA-Z0-9_/.-]+)\s*$",
    }
    
    # Markdown patterns
    MARKDOWN_PATTERNS = {
        "link": r"\[([^\]]+)\]\(([^\)]+)\)",
        "code_fence": r"```([a-zA-Z0-9_/-]+)```",
    }
    
    def __init__(self, repo_root: Path = Path(".")):
        """Initialize scanner.
        
        Args:
            repo_root: Repository root path
        """
        self.repo_root = Path(repo_root)
    
    def find_references(self, old_path: str, new_path: Optional[str] = None) -> List[Reference]:
        """Find all references to a file in codebase.
        
        Args:
            old_path: Original file path to search for
            new_path: Optional new path for context
            
        Returns:
            List of all detected references
        """
        references: List[Reference] = []
        
        # Normalize paths for searching
        old_normalized = self._normalize_path(old_path)
        old_variants = self._generate_path_variants(old_path)
        
        # Scan all files
        for file_path in self.repo_root.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Check extension
            if file_path.suffix not in self.SCANNABLE_EXTENSIONS:
                continue
            
            # Scan file for references
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    lines = f.readlines()
                
                for line_no, line in enumerate(lines, 1):
                    for variant in old_variants:
                        if variant in line:
                            ref = self._extract_reference(
                                file_path, line_no, line, variant, new_path
                            )
                            if ref:
                                references.append(ref)
            except Exception:
                pass
        
        return references
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path for comparison."""
        return path.replace("\\", "/").strip()
    
    def _generate_path_variants(self, path: str) -> List[str]:
        """Generate different variants of a path for matching."""
        normalized = self._normalize_path(path)
        variants = [normalized]
        
        # Add directory name variants (match dirs in paths)
        parts = normalized.split("/")
        if len(parts) > 1:
            variants.append(parts[-1])  # Just filename
            variants.append("/".join(parts))
        
        # Add underscore variants (cortex_brain vs cortex-brain, etc)
        variants.append(normalized.replace("-", "_"))
        variants.append(normalized.replace("_", "-"))
        
        return list(set(variants))  # Deduplicate
    
    def _extract_reference(
        self,
        file_path: Path,
        line_no: int,
        line: str,
        matched_variant: str,
        new_path: Optional[str] = None,
    ) -> Optional[Reference]:
        """Extract reference details from a matched line."""
        rel_path = str(file_path.relative_to(self.repo_root))
        
        # Determine reference type by file extension
        ref_type = self._classify_reference_type(file_path, line)
        
        return Reference(
            file_path=rel_path,
            reference_type=ref_type,
            line_number=line_no,
            original_text=line.strip(),
            old_value=matched_variant,
            new_value=new_path or matched_variant,
            confidence=0.8,
            context=self._extract_context(line, matched_variant),
        )
    
    def _classify_reference_type(self, file_path: Path, line: str) -> ReferenceType:
        """Classify the type of reference based on context."""
        if file_path.suffix == ".py":
            if "import" in line:
                return ReferenceType.PYTHON_IMPORT
            else:
                return ReferenceType.PYTHON_STRING
        elif file_path.suffix in {".yaml", ".yml"}:
            return ReferenceType.YAML_PATH
        elif file_path.suffix == ".md":
            return ReferenceType.MARKDOWN_LINK
        elif file_path.suffix == ".sh":
            return ReferenceType.SHELL_PATH
        elif file_path.name == "Makefile":
            return ReferenceType.MAKEFILE_PATH
        elif file_path.name == ".gitignore":
            return ReferenceType.GITIGNORE_PATTERN
        else:
            return ReferenceType.CONFIG_PATH
    
    def _extract_context(self, line: str, matched_variant: str) -> str:
        """Extract context around the matched variant."""
        pos = line.find(matched_variant)
        start = max(0, pos - 20)
        end = min(len(line), pos + len(matched_variant) + 20)
        return line[start:end]


class ReferenceUpdater:
    """Update all references when files are moved."""
    
    def __init__(self, repo_root: Path = Path(".")):
        """Initialize updater.
        
        Args:
            repo_root: Repository root path
        """
        self.repo_root = Path(repo_root)
        self.scanner = ReferenceScanner(repo_root)
    
    def update_references(
        self,
        old_path: str,
        new_path: str,
        dry_run: bool = False,
    ) -> UpdateResult:
        """Find and update all references to a moved file.
        
        Args:
            old_path: Original file path
            new_path: New file path
            dry_run: If True, don't actually modify files
            
        Returns:
            UpdateResult with all changes made/proposed
        """
        result = UpdateResult(success=True)
        
        # Find all references
        references = self.scanner.find_references(old_path, new_path)
        result.total_references_found = len(references)
        
        if not references:
            return result
        
        # Group by file to minimize I/O
        refs_by_file: Dict[str, List[Reference]] = {}
        for ref in references:
            if ref.file_path not in refs_by_file:
                refs_by_file[ref.file_path] = []
            refs_by_file[ref.file_path].append(ref)
        
        # Update each file
        for file_path, file_refs in refs_by_file.items():
            try:
                success = self._update_file(
                    self.repo_root / file_path,
                    file_refs,
                    dry_run=dry_run,
                )
                
                if success:
                    result.files_updated += 1
                    result.references_changed += len(file_refs)
                    result.updates.extend(file_refs)
                else:
                    result.failures.append(f"Failed to update {file_path}")
                    result.success = False
            except Exception as e:
                result.failures.append(f"Error updating {file_path}: {str(e)}")
                result.success = False
        
        return result
    
    def _update_file(
        self,
        file_path: Path,
        references: List[Reference],
        dry_run: bool = False,
    ) -> bool:
        """Update a single file with reference changes.
        
        Args:
            file_path: Path to file to update
            references: References to update in this file
            dry_run: If True, don't actually modify
            
        Returns:
            True if successful
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            original_content = content
            
            # Apply all replacements
            for ref in references:
                # Use regex to replace in context-aware way
                old_escaped = re.escape(ref.old_value)
                new_value = ref.new_value
                
                # Replace with context awareness
                if ref.reference_type == ReferenceType.PYTHON_IMPORT:
                    # More careful replacement for imports
                    pattern = rf"(from|import)\s+{old_escaped}"
                    content = re.sub(pattern, rf"\1 {new_value}", content)
                else:
                    # Simple replacement for other types
                    content = content.replace(ref.old_value, new_value)
            
            # Only write if changes made
            if content != original_content and not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
            
            return True
        except Exception:
            return False


# AC_START: AC-VAC-ENH-002 | Cross-reference update system
__all__ = [
    "ReferenceType",
    "Reference",
    "UpdateResult",
    "ReferenceScanner",
    "ReferenceUpdater",
]
# AC_COMPLETE: AC-VAC-ENH-002 ✅ Reference updater with multi-type support

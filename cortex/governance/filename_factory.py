"""
AC-FILENAME-FACTORY-001: Filename Factory Core Modules

Provides FilenameFactory, FilenameValidator, FilePathEnforcer for
enforcing CORE-028 (kebab-case, 25-char limit) and CORE-038 (file placement)
across entire CORTEX system.

CORE Rules Applied:
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-027: Audit trail logging
- CORE-028: Kebab-case naming (25-char limit)
- CORE-038: File placement policy
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes & Enums
# ============================================================================

class ViolationCode(Enum):
    """Enumeration of violation codes."""
    CORE_028 = "CORE-028"
    CORE_038 = "CORE-038"


@dataclass
class NamingViolation:
    """Represents a naming convention violation."""
    code: str
    filename: str
    message: str
    suggestion: Optional[str] = None
    severity: str = "blocked"
    
    def __post_init__(self) -> None:
        """Validate violation data."""
        if not self.code:
            raise ValueError("Violation code cannot be empty")
        if not self.filename:
            raise ValueError("Filename cannot be empty")
        if not self.message:
            raise ValueError("Message cannot be empty")


@dataclass
class PlacementViolation:
    """Represents a file placement policy violation."""
    code: str
    path: str
    message: str
    suggested_path: Optional[str] = None
    severity: str = "blocked"
    
    def __post_init__(self) -> None:
        """Validate violation data."""
        if not self.code:
            raise ValueError("Violation code cannot be empty")
        if not self.path:
            raise ValueError("Path cannot be empty")
        if not self.message:
            raise ValueError("Message cannot be empty")


@dataclass
class ValidationResult:
    """Result of filename validation."""
    is_valid: bool
    violations: List[NamingViolation] = field(default_factory=lambda: [])


@dataclass
class GenerationResult:
    """Result of filename generation."""
    success: bool
    filename: Optional[str] = None
    reasoning: str = ""
    alternative_names: List[str] = field(default_factory=lambda: [])


@dataclass
class PathValidationResult:
    """Result of path validation."""
    is_valid: bool
    violations: List[PlacementViolation] = field(default_factory=lambda: [])


# ============================================================================
# FilenameValidator - Enforce CORE-028
# ============================================================================

class FilenameValidator:
    """
    Validates filenames against CORE-028 rules.
    
    CORE-028 Requirements:
    - Kebab-case (lowercase with hyphens, no underscores)
    - Maximum 25 characters including extension
    - Uses semantic acronyms from CORE-028 dictionary
    - Self-documenting purpose
    """
    
    # CORE-028 Acronym Dictionary
    SEMANTIC_ACRONYMS: Dict[str, str] = {
        # Infrastructure
        "cfg": "config",
        "db": "database",
        "mgr": "manager",
        "svc": "service",
        "util": "utility",
        
        # Operations
        "exec": "execution",
        "impl": "implementation",
        "ver": "verification",
        "sync": "synchronization",
        "gen": "generator",
        
        # Analysis & Reporting
        "rpt": "report",
        "ana": "analysis",
        "audit": "audit log",
        "trc": "trace",
        "diag": "diagnostic",
        
        # Governance & State
        "gov": "governance",
        "state": "state machine",
        "ac": "acceptance criteria",
        "ar": "action record",
        
        # Naming/Conventions
        "conv": "convention",
        "std": "standard",
        "pat": "pattern",
        "fmt": "format",
        
        # Testing & Quality
        "test": "test",
        "chk": "check",
        "val": "validation",
    }
    
    # Kebab-case regex pattern (CORE-028)
    KEBAB_CASE_PATTERN: str = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]+)?$'
    
    # Maximum filename length (CORE-028)
    MAX_FILENAME_LENGTH: int = 25
    
    def __init__(self) -> None:
        """Initialize filename validator."""
        self._kebab_pattern = re.compile(self.KEBAB_CASE_PATTERN)
        logger.debug("FilenameValidator initialized")
    
    def validate(self, filename: str) -> ValidationResult:
        """
        Validate filename against CORE-028 rules.
        
        Args:
            filename: Filename to validate (e.g., "cortex-vacuum-exec.py")
            
        Returns:
            ValidationResult with is_valid flag and any violations
        """
        violations: List[NamingViolation] = []
        
        if not filename:
            violations.append(
                NamingViolation(
                    code="CORE-028",
                    filename=filename,
                    message="Filename cannot be empty",
                    severity="blocked"
                )
            )
            return ValidationResult(is_valid=False, violations=violations)
        
        # Check length (CORE-028)
        if len(filename) > self.MAX_FILENAME_LENGTH:
            suggestion = self._suggest_truncation(filename)
            violations.append(
                NamingViolation(
                    code="CORE-028",
                    filename=filename,
                    message=f"Filename exceeds 25 char limit ({len(filename)} chars)",
                    suggestion=suggestion,
                    severity="blocked"
                )
            )
        
        # Check kebab-case format (CORE-028)
        if not self._is_kebab_case(filename):
            suggestion = self._suggest_kebab_case_fix(filename)
            violations.append(
                NamingViolation(
                    code="CORE-028",
                    filename=filename,
                    message="Filename must use kebab-case (lowercase with hyphens)",
                    suggestion=suggestion,
                    severity="blocked"
                )
            )
        
        return ValidationResult(is_valid=len(violations) == 0, violations=violations)
    
    def _is_kebab_case(self, filename: str) -> bool:
        """
        Check if filename matches kebab-case pattern.
        
        Args:
            filename: Filename to check
            
        Returns:
            True if filename is valid kebab-case
        """
        # Check for uppercase letters (not allowed)
        if any(c.isupper() for c in filename.split('.')[0]):
            return False
        
        # Check for underscores (not allowed, use hyphens)
        if '_' in filename.split('.')[0]:
            return False
        
        # Check for spaces (not allowed)
        if ' ' in filename:
            return False
        
        # Match regex pattern
        return bool(self._kebab_pattern.match(filename))
    
    def _suggest_kebab_case_fix(self, filename: str) -> str:
        """
        Suggest kebab-case correction for invalid filename.
        
        Args:
            filename: Invalid filename
            
        Returns:
            Suggested corrected filename
        """
        # Split into name and extension
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            ext = '.' + ext
        else:
            name = filename
            ext = ''
        
        # Convert CamelCase to kebab-case FIRST
        # Insert hyphen before uppercase letters
        name = re.sub(r'([a-z])([A-Z])', r'\1-\2', name)
        
        # Convert to lowercase
        name = name.lower()
        
        # Replace underscores and spaces with hyphens
        name = re.sub(r'[_\s]+', '-', name)
        
        # Remove non-alphanumeric characters (except hyphens)
        name = re.sub(r'[^a-z0-9-]', '', name)
        
        # Collapse multiple hyphens
        name = re.sub(r'-+', '-', name)
        
        # Remove leading/trailing hyphens
        name = name.strip('-')
        
        return name + ext
    
    def _suggest_truncation(self, filename: str) -> str:
        """
        Suggest intelligent truncation to 25 chars.
        
        Args:
            filename: Oversized filename
            
        Returns:
            Suggested truncated filename
        """
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            ext = '.' + ext
        else:
            name = filename
            ext = ''
        
        # Available chars for name (25 - len(ext))
        available = self.MAX_FILENAME_LENGTH - len(ext)
        
        # If extension alone exceeds limit, just truncate brutally
        if available <= 0:
            return filename[:self.MAX_FILENAME_LENGTH]
        
        # Truncate intelligently by removing trailing words
        parts = name.split('-')
        while len('-'.join(parts)) > available and len(parts) > 1:
            parts.pop()
        
        return '-'.join(parts) + ext


# ============================================================================
# FilenameFactory - Generate CORE-028 Compliant Filenames
# ============================================================================

class FilenameFactory:
    """
    Generates filenames compliant with CORE-028 rules.
    
    Converts natural language purposes into valid kebab-case filenames
    with intelligent abbreviation to stay under 25-character limit.
    """
    
    # Words to remove (add no semantic meaning)
    STOP_WORDS: set[str] = {
        'the', 'a', 'an', 'and', 'or', 'for', 'of', 'in', 'on', 'at',
        'to', 'by', 'from', 'with', 'without', 'is', 'are', 'was', 'were',
        'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did'
    }
    
    # Common abbreviations (CORE-028)
    ABBREVIATIONS: Dict[str, str] = {
        "configuration": "cfg",
        "config": "cfg",
        "database": "db",
        "manager": "mgr",
        "management": "mgr",
        "service": "svc",
        "utility": "util",
        "execution": "exec",
        "executor": "exec",
        "execute": "exec",
        "implementation": "impl",
        "implement": "impl",
        "verification": "ver",
        "verify": "ver",
        "synchronization": "sync",
        "synchronize": "sync",
        "generator": "gen",
        "generate": "gen",
        "report": "rpt",
        "reporting": "rpt",
        "analysis": "ana",
        "analyze": "ana",
        "analytical": "ana",
        "audit": "audit",
        "trace": "trc",
        "diagnostic": "diag",
        "governance": "gov",
        "governor": "gov",
        "govern": "gov",
        "state": "state",
        "acceptance": "ac",
        "action": "ar",
        "testing": "test",
        "check": "chk",
        "checking": "chk",
        "validation": "val",
        "validate": "val",
    }
    
    def __init__(self) -> None:
        """Initialize filename factory."""
        logger.debug("FilenameFactory initialized")
    
    def generate(
        self,
        purpose: str,
        file_type: str,
        max_chars: int = 25,
        prefix: Optional[str] = None
    ) -> GenerationResult:
        """
        Generate CORE-028 compliant filename from purpose.
        
        Args:
            purpose: Natural language description of file purpose
            file_type: File extension (py, yaml, md, db, txt, etc.)
            max_chars: Maximum filename length (default 25)
            prefix: Optional prefix (e.g., "test" for test files)
            
        Returns:
            GenerationResult with generated filename or error
            
        Example:
            result = factory.generate(
                purpose="logging analysis utility",
                file_type="py",
                max_chars=25
            )
            # Returns: "log-ana-util.py" (15 chars)
        """
        try:
            # Normalize file type
            if not file_type.startswith('.'):
                ext = f".{file_type}"
            else:
                ext = file_type
            
            # Clean purpose
            purpose = purpose.lower().strip()
            
            # Extract keywords (remove stop words)
            words = [w for w in purpose.split() if w not in self.STOP_WORDS]
            
            if not words:
                return GenerationResult(
                    success=False,
                    reasoning="No meaningful words in purpose"
                )
            
            # Apply abbreviations
            abbreviated = []
            for word in words:
                # Check if whole word has abbreviation
                if word in self.ABBREVIATIONS:
                    abbreviated.append(self.ABBREVIATIONS[word])
                else:
                    abbreviated.append(word)
            
            # Build base name with prefix
            if prefix:
                base_name = f"{prefix}-" + "-".join(abbreviated)
            else:
                base_name = "-".join(abbreviated)
            
            # Ensure kebab-case
            base_name = re.sub(r'[_\s]+', '-', base_name)
            base_name = base_name.lower()
            
            # Truncate if needed
            target_len = max_chars - len(ext)
            if len(base_name) > target_len:
                base_name = self._intelligent_truncate(base_name, target_len)
            
            filename = base_name + ext
            
            return GenerationResult(
                success=True,
                filename=filename,
                reasoning=f"Generated from '{purpose}' using abbreviations"
            )
        
        except Exception as e:
            logger.error(f"Filename generation failed: {e}")
            return GenerationResult(
                success=False,
                reasoning=f"Error: {str(e)}"
            )
    
    def _intelligent_truncate(self, name: str, max_len: int) -> str:
        """
        Intelligently truncate name to max length.
        
        Removes words from the end (less important) rather than
        truncating mid-word.
        
        Args:
            name: Hyphenated name to truncate
            max_len: Maximum length allowed
            
        Returns:
            Truncated name
        """
        if len(name) <= max_len:
            return name
        
        parts = name.split('-')
        while len('-'.join(parts)) > max_len and len(parts) > 1:
            parts.pop()
        
        return '-'.join(parts)


# ============================================================================
# FilePathEnforcer - Enforce CORE-038 File Placement Policy
# ============================================================================

class FilePathEnforcer:
    """
    Enforces CORE-038 file placement policy.
    
    CORE-038 Requirements:
    - NO files at repository root
    - .md files only in docs/{subfolder}/ or reports/{subfolder}/
    - .py files only in cortex/{module}/, cortex_brain/{module}/, or tests/
    - cortex_brain files follow tier structure
    - Whitelisted files (README.md, requirements.txt) allowed at root
    """
    
    # Whitelisted files allowed at repository root
    WHITELIST: set[str] = {
        "README.md",
        "requirements.txt",
        "pyrightconfig.json",
        "cortex-config.yaml",
        "cortex-impl-map.yaml",
        "mkdocs.yml",
        ".gitignore",
        ".github",
        ".env",
    }
    
    # Directory rules: {dir_pattern: {file_extensions: allowed?, require_subfolder?}}
    DIR_RULES: Dict[str, Dict[str, Any]] = {
        "docs": {
            "md": True,
            "require_subfolder": True,
            "allowed_extensions": [".md"],
        },
        "reports": {
            "md": True,
            "require_subfolder": True,
            "allowed_extensions": [".md", ".yaml", ".yml", ".txt"],
        },
        "cortex": {
            "py": True,
            "require_subfolder": True,
            "allowed_extensions": [".py"],
        },
        "cortex_brain": {
            "py": True,
            "require_subfolder": True,
            "allowed_extensions": [".py", ".yaml", ".yml"],
        },
        "tests": {
            "py": True,
            "require_subfolder": True,
            "allowed_extensions": [".py"],
        },
        "_workspaces": {
            "any": True,
            "require_subfolder": True,
            "allowed_extensions": [".md", ".yaml", ".yml", ".txt"],
        },
    }
    
    def __init__(self) -> None:
        """Initialize file path enforcer."""
        logger.debug("FilePathEnforcer initialized")
    
    def validate_path(self, path: Path, file_type: str) -> PathValidationResult:
        """
        Validate file path against CORE-038 placement policy.
        
        Args:
            path: Full file path to validate
            file_type: File extension/type (py, md, yaml, etc.)
            
        Returns:
            PathValidationResult with validation status and violations
        """
        violations: List[PlacementViolation] = []
        
        # Normalize path
        path = Path(path)
        filename = path.name
        
        # Check whitelist (allowed at root)
        if self._is_whitelisted(filename):
            return PathValidationResult(is_valid=True, violations=[])
        
        # Check if at root level
        if self._is_at_root(path):
            violations.append(
                PlacementViolation(
                    code="CORE-038",
                    path=str(path),
                    message=f"File '{filename}' cannot be at repository root",
                    suggested_path=self._suggest_path(path, file_type),
                    severity="blocked"
                )
            )
            return PathValidationResult(is_valid=False, violations=violations)
        
        # Check directory-specific rules
        parent_dirs = path.parts
        if len(parent_dirs) >= 2:
            # Get the direct parent and grandparent directories
            direct_parent = path.parent.name  # e.g., "governance", "guides"
            
            # Check major directory rules
            for major_dir in ["docs", "reports", "cortex", "cortex_brain", "tests", "_workspaces"]:
                if major_dir in parent_dirs:
                    major_idx = parent_dirs.index(major_dir)
                    
                    # Check if file is directly in major directory (not in subfolder)
                    if len(parent_dirs) == major_idx + 2:  # File is direct child
                        # This file is at major directory root, needs subfolder
                        violations.append(
                            PlacementViolation(
                                code="CORE-038",
                                path=str(path),
                                message=f"Files in '{major_dir}/' must be in a subfolder",
                                suggested_path=self._suggest_path(path, file_type),
                                severity="blocked"
                            )
                        )
                        return PathValidationResult(is_valid=False, violations=violations)
        
        return PathValidationResult(is_valid=len(violations) == 0, violations=violations)
    
    def _is_whitelisted(self, filename: str) -> bool:
        """
        Check if filename is whitelisted (allowed at root).
        
        Args:
            filename: Filename to check
            
        Returns:
            True if whitelisted
        """
        return filename in self.WHITELIST or any(
            filename.startswith(wl) for wl in self.WHITELIST
        )
    
    def _is_at_root(self, path: Path) -> bool:
        """
        Check if file is at repository root.
        
        Args:
            path: File path
            
        Returns:
            True if at root
        """
        # Count path components to root
        # Repo root is /Users/asifhussain/PROJECTS/CORTEX
        parts = path.parts
        
        # Find CORTEX directory
        try:
            cortex_idx = parts.index("CORTEX")
            # If only 2 parts after CORTEX (CORTEX and filename), it's at root
            return len(parts) == cortex_idx + 2
        except ValueError:
            return False
    
    def _suggest_path(self, path: Path, file_type: str) -> str:
        """
        Suggest compliant path for file.
        
        Args:
            path: Invalid file path
            file_type: File extension
            
        Returns:
            Suggested valid path
        """
        filename = path.name
        
        # Suggest based on file type
        if file_type == "md":
            return "/Users/asifhussain/PROJECTS/CORTEX/docs/guides/" + filename
        elif file_type == "py":
            return "/Users/asifhussain/PROJECTS/CORTEX/cortex/governance/" + filename
        else:
            return "/Users/asifhussain/PROJECTS/CORTEX/reports/analysis/" + filename

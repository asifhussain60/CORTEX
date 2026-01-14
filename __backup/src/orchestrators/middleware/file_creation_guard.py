"""
FileCreationGuard Middleware - Enforce CORE-002 & CORE-020 Governance Rules

CORE-002: Block Summary/Report/Explanation File Creation
  - Prevents markdown summary files (*-summary.md, *-report.md, etc.)
  - Allows executive summaries ONLY in chat (not as files)
  - Exceptions: Required reports in plan_folder/reports/ and plan_folder/analysis/

CORE-020: Orchestrators Must Not Create Markdown Work Products
  - No markdown files generated as orchestrator output
  - Only structured data (YAML, JSON, Python) allowed
  - Exception: Human-authored documentation (docs/, README.md)

Author: CORTEX Governance System
Version: 1.0.0
Created: 2026-01-12
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional
from functools import wraps
import logging

logger = logging.getLogger(__name__)


class FileCreationGuard:
    """Middleware to enforce CORE-002 and CORE-020 file creation governance rules."""

    # Blocklist patterns (exact matches and regex)
    BLOCKLIST_EXACT = {
        '*-summary.md',
        '*-report.md',
        '*-explanation.md',
        'completion-*.md',
        'executive-summary.md',
        'EXECUTIVE-SUMMARY.md',
    }

    # Regex patterns for blocked file names
    BLOCKLIST_PATTERNS = [
        r'^.*-summary\.md$',
        r'^.*-report\.md$',
        r'^.*-explanation\.md$',
        r'^completion-.*\.md$',
        r'^EXECUTIVE-SUMMARY\.md$',
        r'^executive-summary\.md$',
        r'.*analysis-report\.md$',
        r'.*implementation-summary\.md$',
    ]

    # Allowlist exceptions - these locations CAN create certain markdown files
    ALLOWLIST_PATHS = {
        'cortex-brain/documents/planning/': ['validation-report.md', 'gap-analysis.md'],
        'cortex-brain/documents/': [
            'README.md',
            'ARCHITECTURE.md',
            'DESIGN.md',
        ],
        'docs/': '*',  # All markdown allowed in docs/
        '.github/': '*',  # All markdown allowed in .github/
    }

    # Allowed work product files (structured data, not markdown)
    ALLOWED_EXTENSIONS = {
        '.py',      # Python code
        '.yaml',    # YAML config
        '.yml',     # YAML variant
        '.json',    # JSON data
        '.sql',     # Database scripts
        '.sh',      # Shell scripts
    }

    @classmethod
    def is_blocked(cls, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a file creation is blocked by governance rules.

        Args:
            file_path: Path to the file being created

        Returns:
            Tuple of (is_blocked: bool, reason: str or None)
        """
        path = Path(file_path)
        file_name = path.name

        # Rule 1: Check markdown files (CORE-020 - no markdown work products)
        if path.suffix.lower() == '.md':
            # Check if in allowlist
            for allowed_dir, patterns in cls.ALLOWLIST_PATHS.items():
                if allowed_dir in str(path):
                    if patterns == '*':
                        return False, None
                    if file_name in patterns:
                        return False, None

            # Check if matches blocklist
            for pattern in cls.BLOCKLIST_PATTERNS:
                if re.match(pattern, file_name):
                    return (
                        True,
                        f"CORE-002/CORE-020 VIOLATION: Blocked markdown file '{file_name}'. "
                        f"Use executive summary in chat instead of creating files.",
                    )

            # Check if it's a summary/report/explanation file
            if any(
                keyword in file_name.lower()
                for keyword in ['summary', 'report', 'explanation', 'analysis']
            ):
                if 'cortex-brain/documents/planning' not in str(path):
                    return (
                        True,
                        f"CORE-020 VIOLATION: Blocked markdown work product '{file_name}'. "
                        f"Orchestrators must not create markdown output files.",
                    )

        # Rule 2: Check file naming (CORE-022 - kebab-case, max 20 chars)
        if path.suffix:
            name_only = file_name[: -len(path.suffix)]
        else:
            name_only = file_name

        if not cls._is_valid_file_naming(name_only):
            return (
                True,
                f"CORE-022 VIOLATION: Invalid file naming '{file_name}'. "
                f"Use kebab-case with max 20 characters (excluding extension).",
            )

        return False, None

    @classmethod
    def _is_valid_file_naming(cls, name: str) -> bool:
        """Check if file name follows kebab-case with max 20 char limit."""
        # Allow underscores and numbers (common in Python)
        if not re.match(r'^[a-z0-9_-]+$', name):
            return False

        # Max 20 characters
        if len(name) > 20:
            return False

        return True

    @classmethod
    def validate_before_creation(cls, file_path: str) -> None:
        """
        Validate file creation before it happens.
        Raises FileCreationBlockedException if blocked.

        Args:
            file_path: Path to the file being created

        Raises:
            FileCreationBlockedException: If file creation violates governance
        """
        is_blocked, reason = cls.is_blocked(file_path)
        if is_blocked:
            logger.error(f"🚫 File creation blocked: {reason}")
            raise FileCreationBlockedException(reason)

    @classmethod
    def create_file_safe(
        cls, file_path: str, content: str, force: bool = False
    ) -> Tuple[bool, str]:
        """
        Safely create a file with governance validation.

        Args:
            file_path: Path to the file
            content: File content
            force: Skip governance checks (for emergency bypass)

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not force:
            is_blocked, reason = cls.is_blocked(file_path)
            if is_blocked:
                logger.error(f"🚫 File creation blocked: {reason}")
                return False, reason

        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            Path(file_path).write_text(content)
            logger.info(f"✅ File created: {file_path}")
            return True, f"File created successfully: {file_path}"
        except Exception as e:
            logger.error(f"❌ File creation failed: {e}")
            return False, str(e)

    @classmethod
    def audit_violations(cls, root_dir: str = '.') -> List[Tuple[str, str]]:
        """
        Audit existing files for governance violations.

        Args:
            root_dir: Directory to scan

        Returns:
            List of (file_path, reason) tuples for violated files
        """
        violations = []
        root_path = Path(root_dir)

        for file_path in root_path.rglob('*'):
            if not file_path.is_file():
                continue

            is_blocked, reason = cls.is_blocked(str(file_path))
            if is_blocked:
                violations.append((str(file_path), reason))

        return violations


class FileCreationBlockedException(Exception):
    """Exception raised when file creation is blocked by governance rules."""

    pass


def require_governance_check(func):
    """
    Decorator to add governance check to file creation operations.
    Wraps any function that creates files.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Try to extract file_path from arguments
        file_path = kwargs.get('file_path') or (
            args[1] if len(args) > 1 else None
        )

        if file_path:
            try:
                FileCreationGuard.validate_before_creation(file_path)
            except FileCreationBlockedException as e:
                logger.error(f"Governance violation prevented: {e}")
                raise

        return func(*args, **kwargs)

    return wrapper


# Public API
def block_if_markdown_summary(file_path: str) -> bool:
    """Simple boolean check for markdown summary files."""
    is_blocked, _ = FileCreationGuard.is_blocked(file_path)
    return is_blocked


def get_violations_in_workspace(root_dir: str = '.') -> List[str]:
    """Get list of files violating governance in workspace."""
    violations = FileCreationGuard.audit_violations(root_dir)
    return [f[0] for f in violations]

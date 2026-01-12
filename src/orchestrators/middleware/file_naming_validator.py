"""
FileNamingValidator Middleware - Enforce CORE-022 Governance Rule

CORE-022: Kebab-Case File Naming with 20-Character Limit
  - All files MUST use kebab-case (lowercase, hyphens, underscores, numbers)
  - File name (excluding extension) MUST be ≤20 characters
  - Applies to: Python, YAML, JSON, shell scripts
  - Exceptions: System files, third-party code, auto-generated names

Author: CORTEX Governance System
Version: 1.0.0
Created: 2026-01-12
"""

import re
from pathlib import Path
from typing import List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class FileNamingValidator:
    """Middleware to enforce CORE-022 file naming governance rules."""

    # Maximum length for file name (excluding extension)
    MAX_NAME_LENGTH = 20

    # Allowed patterns (kebab-case)
    KEBAB_CASE_PATTERN = r'^[a-z0-9]+(?:[_-][a-z0-9]+)*$'

    # File types to validate
    VALIDATE_EXTENSIONS = {
        '.py',
        '.yaml',
        '.yml',
        '.json',
        '.sh',
        '.md',
    }

    # Exceptions (files that don't need to follow naming rules)
    EXCEPTIONS = {
        '__init__.py',
        '__main__.py',
        '__pycache__',
        '.gitignore',
        '.gitkeep',
        'README.md',
        'LICENSE',
        'Makefile',
        'requirements.txt',
        'setup.py',
        'conftest.py',
        'pytest.ini',
    }

    @classmethod
    def is_valid(cls, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a file follows naming governance.

        Args:
            file_path: Path to the file

        Returns:
            Tuple of (is_valid: bool, reason: str or None)
        """
        path = Path(file_path)
        file_name = path.name

        # Check if in exceptions
        if file_name in cls.EXCEPTIONS:
            return True, None

        # Only validate specific extensions
        if path.suffix.lower() not in cls.VALIDATE_EXTENSIONS:
            return True, None

        # Extract name without extension
        if path.suffix:
            name_only = file_name[: -len(path.suffix)]
        else:
            name_only = file_name

        # Check kebab-case
        if not re.match(cls.KEBAB_CASE_PATTERN, name_only):
            return (
                False,
                f"CORE-022 VIOLATION: File '{file_name}' does not follow kebab-case. "
                f"Use lowercase letters, numbers, hyphens, and underscores only.",
            )

        # Check length
        if len(name_only) > cls.MAX_NAME_LENGTH:
            return (
                False,
                f"CORE-022 VIOLATION: File '{file_name}' name exceeds {cls.MAX_NAME_LENGTH} characters. "
                f"Current length: {len(name_only)}. Shorten file name.",
            )

        return True, None

    @classmethod
    def validate_file_creation(cls, file_path: str) -> None:
        """
        Validate file naming before creation.
        Raises FileNamingViolation if invalid.

        Args:
            file_path: Path to the file

        Raises:
            FileNamingViolation: If file naming violates CORE-022
        """
        is_valid, reason = cls.is_valid(file_path)
        if not is_valid:
            logger.error(f"🚫 File naming violation: {reason}")
            raise FileNamingViolation(reason)

    @classmethod
    def audit_violations(cls, root_dir: str = '.') -> List[Tuple[str, str]]:
        """
        Audit existing files for naming violations.

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

            # Skip certain directories
            if any(
                part in file_path.parts
                for part in ['__pycache__', '.git', 'node_modules', '.venv', 'venv']
            ):
                continue

            is_valid, reason = cls.is_valid(str(file_path))
            if not is_valid:
                violations.append((str(file_path), reason))

        return violations

    @classmethod
    def suggest_fix(cls, file_path: str) -> str:
        """
        Suggest a valid file name for a violating file.

        Args:
            file_path: Invalid file path

        Returns:
            Suggested valid file name
        """
        path = Path(file_path)
        file_name = path.name

        if path.suffix:
            name_only = file_name[: -len(path.suffix)]
        else:
            name_only = file_name

        # Convert to kebab-case
        # 1. Replace spaces with hyphens
        fixed = name_only.replace(' ', '-')
        # 2. Remove invalid characters
        fixed = re.sub(r'[^a-z0-9_-]', '', fixed.lower())
        # 3. Replace multiple underscores/hyphens with single
        fixed = re.sub(r'[-_]+', '-', fixed)
        # 4. Trim to max length
        if len(fixed) > cls.MAX_NAME_LENGTH:
            fixed = fixed[: cls.MAX_NAME_LENGTH].rstrip('-_')

        return f"{fixed}{path.suffix}"

    @classmethod
    def get_statistics(cls, root_dir: str = '.') -> dict:
        """
        Get statistics on file naming compliance.

        Args:
            root_dir: Directory to scan

        Returns:
            Dictionary with compliance statistics
        """
        root_path = Path(root_dir)
        total_files = 0
        valid_files = 0
        violations = []

        for file_path in root_path.rglob('*'):
            if not file_path.is_file():
                continue

            if any(
                part in file_path.parts
                for part in ['__pycache__', '.git', 'node_modules', '.venv', 'venv']
            ):
                continue

            total_files += 1
            is_valid, reason = cls.is_valid(str(file_path))
            if is_valid:
                valid_files += 1
            else:
                violations.append({
                    'file': str(file_path),
                    'current_name': file_path.name,
                    'suggestion': cls.suggest_fix(str(file_path)),
                    'reason': reason,
                })

        return {
            'total_files': total_files,
            'valid_files': valid_files,
            'violations': len(violations),
            'compliance_percent': (
                (valid_files / total_files * 100) if total_files > 0 else 0
            ),
            'violation_details': violations,
        }


class FileNamingViolation(Exception):
    """Exception raised when file naming violates CORE-022."""

    pass


def validate_file_naming(file_path: str) -> bool:
    """Check if file naming is valid."""
    is_valid, _ = FileNamingValidator.is_valid(file_path)
    return is_valid


def get_naming_violations(root_dir: str = '.') -> List[str]:
    """Get list of files with naming violations."""
    violations = FileNamingValidator.audit_violations(root_dir)
    return [f[0] for f in violations]

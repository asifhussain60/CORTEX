"""
File Write Policy for CORTEX.

Enforces markdown report ban (CORE-002) at file write interception layer.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 specification (AC-29-F6), CORE-002
"""

import re
from pathlib import Path
from typing import Tuple


class MarkdownBanViolation(Exception):
    """Raised when markdown report write is blocked."""
    pass


class ReportIntentDetected(Exception):
    """Raised when report intent is detected."""
    pass


class FileWritePolicy:
    """
    Policy enforcer for file write operations.

    Blocks markdown report generation (CORE-002) while allowing:
    - docs/ directory (product documentation)
    - README.md files (project metadata)
    - .github/ directory (prompts, agents)
    - cortex-registry/ directory (plan tracking)

    Example:
        >>> policy = FileWritePolicy()
        >>> policy.check_write("phase-report.md", content)  # Raises MarkdownBanViolation
        >>> policy.check_write(\".github/prompts/guide.md\", content)    # Returns True
    """

    # Forbidden filename patterns
    REPORT_PATTERNS = [
        r".*report.*\.md$",
        r".*summary.*\.md$",
        r".*completion.*\.md$",
        r".*progress.*\.md$",
        r".*analysis.*\.md$",
        r".*findings.*\.md$",
        r".*results.*\.md$",
    ]

    # Allowed paths (exceptions)
    EXCEPTION_PATTERNS = [
        r"^docs/",
        r"^\.github/",
        r"^cortex-registry/",
        r".*/README\.md$",
        r"^README\.md$",
    ]

    # Report keywords in content
    REPORT_KEYWORDS = [
        "completion report",
        "phase summary",
        "execution report",
        "progress update",
        "analysis report",
        "findings summary",
    ]

    def __init__(self, enforce: bool = True):
        """
        Initialize policy.

        Args:
            enforce: If True, raise exception on violation. If False, warn only.
        """
        self.enforce = enforce

    def is_report_intent(self, file_path: str, content: str = "") -> bool:
        """
        Detect if file write is for reporting/progress/summary.

        Args:
            file_path: Path to file being written
            content: File content (optional, for keyword analysis)

        Returns:
            True if report intent detected
        """
        # Normalize path
        file_path = file_path.replace("\\", "/")

        # Check filename patterns
        for pattern in self.REPORT_PATTERNS:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True

        # Check content keywords (if provided)
        if content:
            content_lower = content.lower()
            for keyword in self.REPORT_KEYWORDS:
                if keyword in content_lower:
                    return True

        return False

    def allow_exception(self, file_path: str) -> bool:
        """
        Check if file path is in allowed exceptions.

        Args:
            file_path: Path to check

        Returns:
            True if exception allowed
        """
        # Normalize path
        file_path = file_path.replace("\\", "/")

        for pattern in self.EXCEPTION_PATTERNS:
            if re.search(pattern, file_path, re.IGNORECASE):
                return True

        return False

    def check_write(self, file_path: str, content: str) -> bool:
        """
        Check if file write is allowed.

        Args:
            file_path: Path to file being written
            content: File content

        Returns:
            True if allowed

        Raises:
            MarkdownBanViolation: If report write is blocked (enforce=True)
        """
        # Check exceptions first
        if self.allow_exception(file_path):
            return True

        # Check for report intent
        if self.is_report_intent(file_path, content):
            if self.enforce:
                raise MarkdownBanViolation(
                    f"CORE-002 violation: Markdown report blocked: {file_path}\n"
                    f"Use inline chat responses only. "
                    f"Allowed: docs/, README.md, .github/, cortex-registry/"
                )
            else:
                # Warn only
                return False

        return True

    def block_markdown_report(self, file_path: str, reason: str) -> None:
        """
        Block markdown report write with detailed reason.

        Args:
            file_path: Path being blocked
            reason: Explanation for blocking

        Raises:
            MarkdownBanViolation: Always raises
        """
        raise MarkdownBanViolation(
            f"Markdown report blocked: {file_path}\n"
            f"Reason: {reason}\n"
            f"Authority: CORE-002 (inline chat only)"
        )

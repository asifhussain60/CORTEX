"""
ResponseFormatter Middleware - Enforce CORE-003 Governance Rule

CORE-003: Executive Summary with Visual Progress Bars Required
  - ALL orchestrator responses MUST provide executive summaries
  - NO code snippets allowed in responses
  - MUST include visual progress bars showing phase completion
  - Response length capped at 40 lines (concise format)

Author: CORTEX Governance System
Version: 1.0.0
Created: 2026-01-12
"""

import re
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Middleware to enforce CORE-003 response formatting requirements."""

    # Visual progress bar characters
    FILLED_BLOCK = '█'
    EMPTY_BLOCK = '░'
    PROGRESS_BAR_WIDTH = 20

    # Validation patterns
    CODE_BLOCK_PATTERN = r'```[\s\S]*?```'
    INLINE_CODE_PATTERN = r'`[^`]+`'

    # Response sections
    REQUIRED_SECTIONS = [
        'OUTCOMES',
        'IN_PROGRESS',
        'RISKS',
        'IMPACT',
    ]

    @classmethod
    def create_progress_bar(cls, filled: int, total: int) -> str:
        """
        Create a visual progress bar.

        Args:
            filled: Number of filled segments
            total: Total segments

        Returns:
            Visual progress bar string
        """
        if total == 0:
            percent = 0
        else:
            percent = int((filled / total) * 100)

        filled_blocks = int((filled / total) * cls.PROGRESS_BAR_WIDTH)
        empty_blocks = cls.PROGRESS_BAR_WIDTH - filled_blocks

        bar = cls.FILLED_BLOCK * filled_blocks + cls.EMPTY_BLOCK * empty_blocks
        return f"{bar} {percent}% ({filled}/{total})"

    @classmethod
    def validate_no_code_blocks(cls, response: str) -> tuple[bool, Optional[str]]:
        """
        Check if response contains code blocks (forbidden).

        Args:
            response: Response text

        Returns:
            Tuple of (is_valid: bool, issue: str or None)
        """
        code_blocks = re.findall(cls.CODE_BLOCK_PATTERN, response)

        if code_blocks:
            return (
                False,
                f"CORE-003 VIOLATION: Response contains {len(code_blocks)} code block(s). "
                f"Remove code snippets - use executive summary format only.",
            )

        return True, None

    @classmethod
    def validate_response_length(cls, response: str) -> tuple[bool, Optional[str]]:
        """
        Check if response respects length limits.

        Args:
            response: Response text

        Returns:
            Tuple of (is_valid: bool, issue: str or None)
        """
        lines = response.split('\n')
        line_count = len(lines)

        if line_count > 40:
            return (
                False,
                f"CORE-003 VIOLATION: Response exceeds 40 lines ({line_count} lines). "
                f"Trim to executive summary format.",
            )

        return True, None

    @classmethod
    def validate_has_progress_bars(cls, response: str) -> tuple[bool, Optional[str]]:
        """
        Check if response includes visual progress bars.

        Args:
            response: Response text

        Returns:
            Tuple of (is_valid: bool, issue: str or None)
        """
        if '█' not in response and '░' not in response:
            return (
                False,
                "CORE-003 VIOLATION: Response missing visual progress bars. "
                "Include progress indicators for phase completion.",
            )

        return True, None

    @classmethod
    def validate_executive_summary_format(
        cls, response: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if response follows executive summary format.

        Args:
            response: Response text

        Returns:
            Tuple of (is_valid: bool, issue: str or None)
        """
        # Check for section headers
        sections_found = []
        for section in cls.REQUIRED_SECTIONS:
            if section in response.upper():
                sections_found.append(section)

        if len(sections_found) < 3:
            return (
                False,
                f"CORE-003 VIOLATION: Response missing required sections. "
                f"Found {len(sections_found)}, need: {', '.join(cls.REQUIRED_SECTIONS)}",
            )

        return True, None

    @classmethod
    def validate_response(cls, response: str) -> tuple[bool, List[str]]:
        """
        Validate response against all CORE-003 requirements.

        Args:
            response: Response text

        Returns:
            Tuple of (is_valid: bool, issues: List[str])
        """
        issues = []

        # Check 1: No code blocks
        valid, issue = cls.validate_no_code_blocks(response)
        if not valid:
            issues.append(issue)

        # Check 2: Response length
        valid, issue = cls.validate_response_length(response)
        if not valid:
            issues.append(issue)

        # Check 3: Has progress bars
        valid, issue = cls.validate_has_progress_bars(response)
        if not valid:
            issues.append(issue)

        # Check 4: Executive summary format
        valid, issue = cls.validate_executive_summary_format(response)
        if not valid:
            issues.append(issue)

        return len(issues) == 0, issues

    @classmethod
    def format_outcome_bullet(cls, text: str, status: str = '✅') -> str:
        """Format an outcome bullet point."""
        return f"{status} {text}"

    @classmethod
    def format_risk_bullet(cls, text: str) -> str:
        """Format a risk bullet point."""
        return f"⚠️  {text}"

    @classmethod
    def format_impact_bullet(cls, text: str) -> str:
        """Format an impact bullet point."""
        return f"🎯 {text}"

    @classmethod
    def create_executive_summary(
        cls,
        outcomes: List[str],
        in_progress: List[str],
        risks: List[str],
        impact: List[str],
        progress_filled: int = 0,
        progress_total: int = 100,
    ) -> str:
        """
        Create a properly formatted executive summary response.

        Args:
            outcomes: List of completed outcomes
            in_progress: List of in-progress items
            risks: List of identified risks
            impact: List of business impact items
            progress_filled: Completed progress segments
            progress_total: Total progress segments

        Returns:
            Formatted response string
        """
        sections = []

        # Progress bar
        progress_bar = cls.create_progress_bar(progress_filled, progress_total)
        sections.append(f"Phase Progress: {progress_bar}\n")

        # Outcomes
        if outcomes:
            sections.append("✅ OUTCOMES")
            for outcome in outcomes:
                sections.append(f"  • {outcome}")
            sections.append("")

        # In Progress
        if in_progress:
            sections.append("⚙️ IN PROGRESS")
            for item in in_progress:
                sections.append(f"  • {item}")
            sections.append("")

        # Risks
        if risks:
            sections.append("⚠️ RISKS")
            for risk in risks:
                sections.append(f"  • {risk}")
            sections.append("")
        else:
            sections.append("⚠️ RISKS")
            sections.append("  • None detected")
            sections.append("")

        # Impact
        if impact:
            sections.append("🎯 IMPACT")
            for item in impact:
                sections.append(f"  • {item}")

        response = '\n'.join(sections)

        # Validate response
        is_valid, issues = cls.validate_response(response)
        if not is_valid:
            logger.warning(f"Response validation issues: {issues}")

        return response


class ResponseFormattingError(Exception):
    """Exception raised when response formatting violates CORE-003."""

    pass


def format_executive_summary(
    outcomes: List[str],
    in_progress: List[str],
    risks: List[str],
    impact: List[str],
    progress: tuple = (0, 100),
) -> str:
    """Create and return a properly formatted executive summary."""
    return ResponseFormatter.create_executive_summary(
        outcomes=outcomes,
        in_progress=in_progress,
        risks=risks,
        impact=impact,
        progress_filled=progress[0],
        progress_total=progress[1],
    )


def validate_response_format(response: str) -> bool:
    """Check if response meets CORE-003 requirements."""
    is_valid, _ = ResponseFormatter.validate_response(response)
    return is_valid

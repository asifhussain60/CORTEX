"""
Response Format Validator.

Advanced response format validation including status icons,
linear narrative flow, markdown structure, and compliance checking.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 Stage 1 specification
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FormatError(Exception):
    """Base exception for format errors."""
    pass


class StatusIcon(Enum):
    """Status icon types with emoji values."""
    COMPLETED = "🟢"
    IN_PROGRESS = "🔵"
    PLANNED = "⚪"
    WARNING = "🟡"
    CRITICAL = "🔴"
    SUCCESS = "✅"
    FAILED = "❌"
    ATTENTION = "⚠️"


class ViolationSeverity(Enum):
    """Violation severity levels."""
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class FormatViolation:
    """
    Format violation report.

    Attributes:
        severity: Violation severity
        message: Violation description
        location: Location in response
        rule_id: Format rule identifier
    """
    severity: ViolationSeverity
    message: str
    location: str
    rule_id: str


@dataclass
class ValidationResult:
    """
    Format validation result.

    Attributes:
        is_valid: Whether format is valid
        violations: List of violations
        score: Quality score (0-1)
        suggestions: Improvement suggestions
    """
    is_valid: bool
    violations: List[FormatViolation]
    score: float
    suggestions: List[str] = field(default_factory=list)


class ResponseFormatValidator:
    """
    Response Format Validator.

    Validates responses against response-format-standards.md rules.
    """

    # Required header pattern
    HEADER_PATTERN = r"##\s*🧠\s*CORTEX"

    # Completion indicators
    COMPLETION_KEYWORDS = ["complete", "completed", "finished", "done"]
    FUTURE_KEYWORDS = ["will", "planning", "going to", "need to", "todo"]

    # Repetition threshold
    REPETITION_THRESHOLD = 0.7  # 70% similarity triggers warning

    def __init__(self):
        """Initialize validator."""
        logger.info("ResponseFormatValidator initialized")

    def validate(self, response: Optional[str]) -> ValidationResult:
        """
        Validate response format comprehensively.

        Args:
            response: Response text to validate

        Returns:
            ValidationResult: Validation result with violations and score
        """
        if not response or not isinstance(response, str):
            return ValidationResult(
                is_valid=False,
                violations=[FormatViolation(
                    ViolationSeverity.ERROR,
                    "Invalid or empty response",
                    "input",
                    "FMT-000",
                )],
                score=0.0,
            )

        violations = []
        suggestions = []

        # Check header
        if not re.search(self.HEADER_PATTERN, response):
            violations.append(FormatViolation(
                ViolationSeverity.ERROR,
                "Missing CORTEX response header",
                "start",
                "FMT-001",
            ))

        # Run all validation checks
        violations.extend(self.validate_status_icons(response).violations)
        violations.extend(self.validate_narrative_flow(response).violations)
        violations.extend(self.validate_numbered_prompts(response).violations)
        violations.extend(self.validate_exit_options(response).violations)
        violations.extend(self.validate_markdown_structure(response).violations)
        violations.extend(self.validate_completion_indicators(response).violations)
        violations.extend(self.detect_repetition(response).violations)

        # Calculate score
        score = self._calculate_score(violations, len(response))

        # Determine validity
        error_count = sum(1 for v in violations if v.severity == ViolationSeverity.ERROR)
        is_valid = error_count == 0 and score >= 0.7

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            score=score,
            suggestions=suggestions,
        )

    def validate_status_icons(self, response: str) -> ValidationResult:
        """
        Validate status icon usage.

        Args:
            response: Response text

        Returns:
            ValidationResult: Icon usage violations
        """
        violations = []

        # Check for ✅ used with future tense
        lines = response.split('\n')
        for i, line in enumerate(lines):
            if StatusIcon.SUCCESS.value in line:
                # Check if line contains future tense keywords
                line_lower = line.lower()
                if any(keyword in line_lower for keyword in self.FUTURE_KEYWORDS):
                    violations.append(FormatViolation(
                        ViolationSeverity.WARNING,
                        f"✅ used with future tense: '{line.strip()}'",
                        f"line {i+1}",
                        "FMT-010",
                    ))

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            score=1.0 if len(violations) == 0 else 0.8,
        )

    def validate_narrative_flow(self, response: str) -> ValidationResult:
        """
        Validate linear narrative flow (Context → Analysis → Action → Result).

        Args:
            response: Response text

        Returns:
            ValidationResult: Narrative flow violations
        """
        violations = []

        # Check for repeated sections
        sections = re.findall(r'###\s+(.+)', response)
        seen_sections = {}
        for section in sections:
            section_normalized = section.lower().strip()
            if section_normalized in seen_sections:
                violations.append(FormatViolation(
                    ViolationSeverity.WARNING,
                    f"Repeated section: '{section}'",
                    f"section {section}",
                    "FMT-020",
                ))
            seen_sections[section_normalized] = True

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            score=1.0 if len(violations) == 0 else 0.7,
        )

    def validate_numbered_prompts(self, response: str) -> ValidationResult:
        """
        Validate numbered prompt usage (only for decision points).

        Args:
            response: Response text

        Returns:
            ValidationResult: Numbered prompt violations
        """
        violations = []

        # Check for numbered emojis after completion
        has_completion = any(keyword in response.lower() for keyword in self.COMPLETION_KEYWORDS)
        has_numbers = bool(re.search(r'[1-9]️⃣', response))

        if has_completion and has_numbers:
            # Check if numbers appear after completion statement
            completion_pos = max(response.lower().find(kw) for kw in self.COMPLETION_KEYWORDS if kw in response.lower())
            number_pos = re.search(r'[1-9]️⃣', response)

            if number_pos and number_pos.start() > completion_pos:
                violations.append(FormatViolation(
                    ViolationSeverity.WARNING,
                    "Numbered prompts after completion (should only be for decisions)",
                    f"position {number_pos.start()}",
                    "FMT-030",
                ))

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            score=1.0 if len(violations) == 0 else 0.9,
        )

    def validate_exit_options(self, response: str) -> ValidationResult:
        """
        Validate no exit options during holistic implementation.

        Args:
            response: Response text

        Returns:
            ValidationResult: Exit option violations
        """
        violations = []

        # Check for in-progress indicator with exit options
        has_in_progress = StatusIcon.IN_PROGRESS.value in response
        exit_keywords = ["exit", "pause", "stop", "cancel"]

        if has_in_progress:
            response_lower = response.lower()
            for keyword in exit_keywords:
                if keyword in response_lower:
                    violations.append(FormatViolation(
                        ViolationSeverity.ERROR,
                        f"Exit option '{keyword}' during active implementation",
                        "content",
                        "FMT-040",
                    ))
                    break

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            score=1.0 if len(violations) == 0 else 0.6,
        )

    def validate_markdown_structure(self, response: str) -> ValidationResult:
        """
        Validate markdown structure (headers, tables, code blocks).

        Args:
            response: Response text

        Returns:
            ValidationResult: Structure violations
        """
        violations = []

        # Check header hierarchy
        headers = re.findall(r'^(#{2,6})\s+', response, re.MULTILINE)
        if headers:
            prev_level = len(headers[0])
            for i, header in enumerate(headers[1:], 1):
                level = len(header)
                # Check for skipped levels (e.g., ## → #####)
                if level > prev_level + 1:
                    violations.append(FormatViolation(
                        ViolationSeverity.INFO,
                        f"Skipped header level from {'#' * prev_level} to {'#' * level}",
                        f"header {i}",
                        "FMT-050",
                    ))
                prev_level = level

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            score=1.0 if len(violations) == 0 else 0.95,
        )

    def validate_completion_indicators(self, response: str) -> ValidationResult:
        """
        Validate completion indicators vs "Next Steps".

        Args:
            response: Response text

        Returns:
            ValidationResult: Completion indicator violations
        """
        violations = []

        # Check for ✅ with future tense (misleading checkmarks)
        lines = response.split('\n')
        for i, line in enumerate(lines):
            if StatusIcon.SUCCESS.value in line:
                line_lower = line.lower()
                if any(kw in line_lower for kw in self.FUTURE_KEYWORDS):
                    violations.append(FormatViolation(
                        ViolationSeverity.ERROR,
                        f"Misleading ✅ with future tense: '{line.strip()}'",
                        f"line {i+1}",
                        "FMT-061",
                    ))

        # Check for contradictions
        has_completion = StatusIcon.SUCCESS.value in response or any(
            kw in response.lower() for kw in ["implementation complete", "stage complete"]
        )
        has_next_steps = "next steps" in response.lower() or "need to" in response.lower()

        if has_completion and has_next_steps:
            # Check if next steps indicate incomplete work
            if any(kw in response.lower() for kw in ["need to implement", "will add", "todo"]):
                violations.append(FormatViolation(
                    ViolationSeverity.ERROR,
                    "Claims completion but lists incomplete work in Next Steps",
                    "content",
                    "FMT-060",
                ))

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            score=1.0 if len(violations) == 0 else 0.7,
        )

    def detect_repetition(self, response: str) -> ValidationResult:
        """
        Detect repetitive content.

        Args:
            response: Response text

        Returns:
            ValidationResult: Repetition violations
        """
        violations = []

        # Check for exact duplicate lines
        lines = [line.strip() for line in response.split('\n') if len(line.strip()) > 10]
        seen_lines = {}
        for i, line in enumerate(lines):
            if line in seen_lines:
                violations.append(FormatViolation(
                    ViolationSeverity.WARNING,
                    f"Duplicate line detected: '{line[:50]}...'",
                    f"lines {seen_lines[line]} and {i}",
                    "FMT-071",
                ))
            seen_lines[line] = i

        # Split into sentences
        sentences = re.split(r'[.!?]\s+', response)

        # Check for very similar sentences
        for i, sent1 in enumerate(sentences):
            if len(sent1.strip()) < 20:  # Skip short sentences
                continue
            for j, sent2 in enumerate(sentences[i+1:i+5], i+1):  # Check next 4 sentences
                if len(sent2.strip()) < 20:
                    continue
                similarity = self._calculate_similarity(sent1, sent2)
                if similarity > self.REPETITION_THRESHOLD:
                    violations.append(FormatViolation(
                        ViolationSeverity.WARNING,
                        f"Repetitive content detected (similarity: {similarity:.0%})",
                        f"sentences {i} and {j}",
                        "FMT-070",
                    ))
                    break

        return ValidationResult(
            is_valid=len(violations) == 0,
            violations=violations,
            score=1.0 if len(violations) == 0 else 0.8,
        )

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using simple word overlap.

        Args:
            text1: First text
            text2: Second text

        Returns:
            float: Similarity score (0-1)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union) if union else 0.0

    def _calculate_score(self, violations: List[FormatViolation], response_length: int) -> float:
        """
        Calculate overall format quality score.

        Args:
            violations: List of violations
            response_length: Response length

        Returns:
            float: Quality score (0-1)
        """
        if not violations:
            return 1.0

        # Base score
        score = 1.0

        # Deduct for violations
        for violation in violations:
            if violation.severity == ViolationSeverity.ERROR:
                score -= 0.20  # Increased from 0.15
            elif violation.severity == ViolationSeverity.WARNING:
                score -= 0.08  # Increased from 0.05
            else:  # INFO
                score -= 0.02

        # Ensure score stays in valid range
        return max(0.0, min(1.0, score))

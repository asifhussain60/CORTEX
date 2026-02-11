"""
Response Optimizer.

Auto-correction, context flow optimization, and advanced
violation handling for response formatting.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 29 Stage 2 specification
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from cortex.brain.core.response_format_validator import (
    ResponseFormatValidator,
    StatusIcon,
    ValidationResult,
)

logger = logging.getLogger(__name__)


class OptimizerError(Exception):
    """Base exception for optimizer errors."""
    pass


class CorrectionType(Enum):
    """Types of corrections applied."""
    HEADER_ADDED = "HEADER_ADDED"
    ICON_FIXED = "ICON_FIXED"
    REPETITION_REMOVED = "REPETITION_REMOVED"
    FLOW_IMPROVED = "FLOW_IMPROVED"
    EXIT_REMOVED = "EXIT_REMOVED"
    NUMBERS_REMOVED = "NUMBERS_REMOVED"
    SECTION_CONSOLIDATED = "SECTION_CONSOLIDATED"


@dataclass
class Correction:
    """
    Correction applied to response.

    Attributes:
        correction_type: Type of correction
        original: Original text
        corrected: Corrected text
        location: Location of correction
    """
    correction_type: CorrectionType
    original: str
    corrected: str
    location: str


@dataclass
class FlowAnalysis:
    """
    Flow structure analysis.

    Attributes:
        has_context: Has context section
        has_analysis: Has analysis section
        has_action: Has action section
        has_result: Has result section
        flow_score: Flow quality score (0-1)
    """
    has_context: bool
    has_analysis: bool
    has_action: bool
    has_result: bool
    flow_score: float


@dataclass
class OptimizationResult:
    """
    Optimization result.

    Attributes:
        original_text: Original response
        optimized_text: Optimized response
        corrections: List of corrections applied
        improvement_score: Improvement score (0-1)
    """
    original_text: str
    optimized_text: str
    corrections: List[Correction]
    improvement_score: float


class ResponseOptimizer:
    """
    Response Optimizer.

    Automatically corrects common formatting violations and
    optimizes response structure.
    """

    HEADER_TEMPLATE = """## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅

---

"""

    def __init__(self):
        """Initialize optimizer."""
        self.validator = ResponseFormatValidator()
        logger.info("ResponseOptimizer initialized")

    def optimize(
        self,
        response: str,
        orchestrator: str = "MasterOrchestrator",
        improve_flow: bool = True,
    ) -> OptimizationResult:
        """
        Optimize response format.

        Args:
            response: Response to optimize
            orchestrator: Orchestrator name for header
            improve_flow: Whether to improve flow structure

        Returns:
            OptimizationResult: Optimization result
        """
        if not response:
            response = "No content provided."

        original_text = response
        optimized_text = response
        corrections = []

        # 1. Add header if missing
        if not re.search(r"##\s*🧠\s*CORTEX", optimized_text):
            header = self.HEADER_TEMPLATE.format(orchestrator=orchestrator)
            optimized_text = header + optimized_text
            corrections.append(Correction(
                CorrectionType.HEADER_ADDED,
                original_text[:50],
                header + original_text[:50],
                "start",
            ))

        # 2. Fix misleading checkmarks
        fixed_text, icon_corrections = self._fix_misleading_icons(optimized_text)
        optimized_text = fixed_text
        corrections.extend(icon_corrections)

        # 3. Remove duplicate sections
        fixed_text, dup_corrections = self._remove_duplicate_sections(optimized_text)
        optimized_text = fixed_text
        corrections.extend(dup_corrections)

        # 4. Remove exit options during implementation
        fixed_text, exit_corrections = self._remove_exit_options(optimized_text)
        optimized_text = fixed_text
        corrections.extend(exit_corrections)

        # 5. Remove numbered prompts after completion
        fixed_text, num_corrections = self._fix_numbered_prompts(optimized_text)
        optimized_text = fixed_text
        corrections.extend(num_corrections)

        # 6. Remove duplicate lines
        fixed_text, rep_corrections = self._remove_repetition(optimized_text)
        optimized_text = fixed_text
        corrections.extend(rep_corrections)

        # 7. Improve flow if requested
        if improve_flow:
            flow_analysis = self.analyze_flow(optimized_text)
            # Flow improvement is passive for now

        # Calculate improvement score
        improvement_score = self._calculate_improvement(original_text, optimized_text)

        return OptimizationResult(
            original_text=original_text,
            optimized_text=optimized_text,
            corrections=corrections,
            improvement_score=improvement_score,
        )

    def analyze_flow(self, response: str) -> FlowAnalysis:
        """
        Analyze response flow structure.

        Args:
            response: Response to analyze

        Returns:
            FlowAnalysis: Flow analysis result
        """
        response_lower = response.lower()

        # Check for flow components
        has_context = any(kw in response_lower for kw in ["context", "background", "overview"])
        has_analysis = any(kw in response_lower for kw in ["analysis", "examination", "review"])
        has_action = any(kw in response_lower for kw in ["action", "implementation", "approach"])
        has_result = any(kw in response_lower for kw in ["result", "outcome", "complete"])

        # Calculate flow score
        components = [has_context, has_analysis, has_action, has_result]
        flow_score = sum(components) / len(components)

        return FlowAnalysis(
            has_context=has_context,
            has_analysis=has_analysis,
            has_action=has_action,
            has_result=has_result,
            flow_score=flow_score,
        )

    def generate_report(self, result: OptimizationResult) -> str:
        """
        Generate optimization report.

        Args:
            result: Optimization result

        Returns:
            str: Human-readable report
        """
        report_lines = [
            "### Optimization Report",
            f"- Corrections Applied: {len(result.corrections)}",
            f"- Improvement Score: {result.improvement_score:.2%}",
            "",
        ]

        if result.corrections:
            report_lines.append("#### Corrections:")
            for correction in result.corrections:
                report_lines.append(f"- {correction.correction_type.value} at {correction.location}")

        return "\n".join(report_lines)

    def _fix_misleading_icons(self, text: str) -> tuple[str, List[Correction]]:
        """Fix misleading status icons."""
        corrections = []
        lines = text.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            if StatusIcon.SUCCESS.value in line:
                # Check for future tense
                line_lower = line.lower()
                if any(kw in line_lower for kw in ["will", "planning", "going to", "need to"]):
                    # Replace ✅ with ⚪ for planned work
                    fixed_line = line.replace(StatusIcon.SUCCESS.value, StatusIcon.PLANNED.value)
                    fixed_lines.append(fixed_line)
                    corrections.append(Correction(
                        CorrectionType.ICON_FIXED,
                        line,
                        fixed_line,
                        f"line {i}",
                    ))
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines), corrections

    def _remove_duplicate_sections(self, text: str) -> tuple[str, List[Correction]]:
        """Remove duplicate section headers."""
        corrections = []

        # Find all section headers
        sections = re.findall(r'(###\s+.+)', text)
        seen_sections = set()

        for section in sections:
            section_normalized = section.lower().strip()
            if section_normalized in seen_sections:
                # Remove duplicate
                text = text.replace(section, "", 1)
                corrections.append(Correction(
                    CorrectionType.REPETITION_REMOVED,
                    section,
                    "",
                    "section",
                ))
            seen_sections.add(section_normalized)

        return text, corrections

    def _remove_exit_options(self, text: str) -> tuple[str, List[Correction]]:
        """Remove exit options during implementation."""
        corrections = []

        # Check if in progress
        if StatusIcon.IN_PROGRESS.value in text:
            # Remove exit-related lines
            lines = text.split('\n')
            fixed_lines = []

            for line in lines:
                line_lower = line.lower()
                if any(kw in line_lower for kw in ["exit", "pause", "stop", "cancel"]):
                    # Skip this line
                    corrections.append(Correction(
                        CorrectionType.EXIT_REMOVED,
                        line,
                        "",
                        "exit option",
                    ))
                else:
                    fixed_lines.append(line)

            text = '\n'.join(fixed_lines)

        return text, corrections

    def _fix_numbered_prompts(self, text: str) -> tuple[str, List[Correction]]:
        """Fix numbered prompts after completion."""
        corrections = []

        # Check if has completion
        if "complete" in text.lower() or StatusIcon.SUCCESS.value in text:
            # Find position of completion
            completion_keywords = ["complete", "finished", "done"]
            completion_pos = -1
            for kw in completion_keywords:
                pos = text.lower().find(kw)
                if pos > completion_pos:
                    completion_pos = pos

            if completion_pos > 0:
                # Check for numbered emojis after completion
                after_completion = text[completion_pos:]
                numbered_emojis = re.findall(r'[1-9]️⃣', after_completion)

                # Only remove if not in a "Decision" section
                if numbered_emojis and "decision" not in after_completion.lower():
                    # Remove numbered emojis after completion
                    for emoji in set(numbered_emojis):
                        after_completion = after_completion.replace(emoji, "•")

                    text = text[:completion_pos] + after_completion
                    corrections.append(Correction(
                        CorrectionType.NUMBERS_REMOVED,
                        "numbered prompts after completion",
                        "bullet points",
                        "post-completion",
                    ))

        return text, corrections

    def _remove_repetition(self, text: str) -> tuple[str, List[Correction]]:
        """Remove repetitive lines."""
        corrections = []
        lines = text.split('\n')
        seen_lines = set()
        unique_lines = []

        for line in lines:
            line_stripped = line.strip()
            if len(line_stripped) < 10:  # Keep short lines
                unique_lines.append(line)
                continue

            if line_stripped in seen_lines:
                corrections.append(Correction(
                    CorrectionType.REPETITION_REMOVED,
                    line,
                    "",
                    "duplicate line",
                ))
            else:
                unique_lines.append(line)
                seen_lines.add(line_stripped)

        return '\n'.join(unique_lines), corrections

    def _calculate_improvement(self, original: str, optimized: str) -> float:
        """Calculate improvement score."""
        if original == optimized:
            return 0.0

        # Validate both versions
        original_result = self.validator.validate(original)
        optimized_result = self.validator.validate(optimized)

        # Calculate improvement
        improvement = optimized_result.score - original_result.score

        return max(0.0, min(1.0, improvement))

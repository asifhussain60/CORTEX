"""
Chainable Template Blocks for CORTEX Response Composition.

Provides reusable, composable blocks that can be chained together
to build complex responses without repetition. Each block is self-contained
and can be combined with others for flexible response generation.

Module: cortex.orchestrators.response.chainable_blocks
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
Authority: ENH-064 Response Template Migration
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from cortex.orchestrators.core.base_response_template import ContentZone

# ============================================================================
# BLOCK TYPES
# ============================================================================


class BlockType(str, Enum):
    """Type of template block."""

    HEADER = "header"
    ANALYSIS = "analysis"
    METRICS = "metrics"
    RECOMMENDATIONS = "recommendations"
    VALIDATION = "validation"
    NEXT_STEPS = "next_steps"


# ============================================================================
# CHAINABLE BLOCKS
# ============================================================================


class ChainableBlock:
    """
    Base class for chainable template blocks.

    Each block is self-contained and can be chained with others
    using the + operator or compose() method.
    """

    def __init__(self, content: str = "", zone: Optional[ContentZone] = None):
        self.content = content
        self.zone = zone

    def __add__(self, other: 'ChainableBlock') -> 'ChainableBlock':
        """Chain blocks using + operator."""
        return ChainableBlock(self.content + "\n" + other.content)

    def render(self) -> str:
        """Render block content."""
        return self.content

    def is_empty(self) -> bool:
        """Check if block is empty."""
        return not self.content.strip()

    def get_zone(self) -> Optional[ContentZone]:
        """Get content zone for this block."""
        return self.zone


# ============================================================================
# COMMON BLOCKS
# ============================================================================


class TestResultsBlock(ChainableBlock):
    """Block for displaying test results."""

    def __init__(self, tests: List[Dict[str, Any]], title: str = "Test Results"):
        """
        Create test results block.

        Args:
            tests: List of test dicts with name, passed, duration_ms
            title: Section title
        """
        if not tests:
            content = f"\n## 🧪 {title}\n\n_No tests executed._\n"
        else:
            passing = sum(1 for t in tests if t.get("passed", False))
            total = len(tests)

            content = f"\n## 🧪 {title}\n\n**Status:** {passing}/{total} tests passing\n\n"
            content += "| Test | Status | Duration |\n"
            content += "|------|--------|----------|\n"

            for test in tests:
                status = "✅" if test.get("passed") else "❌"
                name = test.get("name", "Unknown")
                duration = test.get("duration_ms", 0)
                content += f"| {name} | {status} | {duration}ms |\n"

        super().__init__(content)


class CoverageMetricsBlock(ChainableBlock):
    """Block for displaying coverage metrics."""

    def __init__(self, metrics: Dict[str, float], title: str = "Coverage Metrics"):
        """
        Create coverage metrics block.

        Args:
            metrics: Dict of metric name -> percentage
            title: Section title
        """
        if not metrics:
            content = f"\n### {title}\n\n_No coverage data available._\n"
        else:
            content = f"\n### {title}\n\n"
            content += "| Metric | Coverage | Status |\n"
            content += "|--------|----------|--------|\n"

            for metric, value in metrics.items():
                status = "✅" if value >= 80 else "⚠️" if value >= 60 else "❌"
                content += f"| {metric} | {value:.1f}% | {status} |\n"

        super().__init__(content)


class ProblemSolutionBlock(ChainableBlock):
    """Block for displaying problem/solution pairs."""

    def __init__(
        self,
        pairs: List[Tuple[str, str]],
        title: str = "Issues & Solutions",
        problem_header: str = "🔴 **Problem**",
        solution_header: str = "🟢 **Solution**"
    ):
        """
        Create problem/solution block.

        Args:
            pairs: List of (problem, solution) tuples
            title: Section title
            problem_header: Problem column header
            solution_header: Solution column header
        """
        if not pairs:
            content = f"\n## {title}\n\n_No issues detected._\n"
        else:
            content = f"\n## {title}\n\n"
            content += f"| {problem_header} | {solution_header} |\n"
            content += "|----------------|------------------|\n"

            for problem, solution in pairs:
                content += f"| {problem} | {solution} |\n"

        super().__init__(content)


class ValidationChecklistBlock(ChainableBlock):
    """Block for displaying validation checklist."""

    def __init__(self, checks: Dict[str, bool], title: str = "Validation Results"):
        """
        Create validation checklist block.

        Args:
            checks: Dict of check name -> passed
            title: Section title
        """
        if not checks:
            content = f"\n## ✅ {title}\n\n_No validation checks defined._\n"
        else:
            content = f"\n## ✅ {title}\n\n"

            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                content += f"- [{status}] {check}\n"

        super().__init__(content)


class MetricsDashboardBlock(ChainableBlock):
    """Block for displaying metrics dashboard."""

    def __init__(
        self,
        metrics: Dict[str, Any],
        title: str = "Metrics Dashboard",
        show_targets: bool = True
    ):
        """
        Create metrics dashboard block.

        Args:
            metrics: Dict of metric name -> {value, target, status}
            title: Section title
            show_targets: Whether to show target column
        """
        if not metrics:
            content = f"\n## 📊 {title}\n\n_No metrics available._\n"
        else:
            content = f"\n## 📊 {title}\n\n"

            if show_targets:
                content += "| Metric | Value | Target | Status |\n"
                content += "|--------|-------|--------|--------|\n"

                for metric, data in metrics.items():
                    value = data.get("value", "N/A")
                    target = data.get("target", "N/A")
                    status = data.get("status", "⚪")
                    content += f"| {metric} | {value} | {target} | {status} |\n"
            else:
                content += "| Metric | Value | Status |\n"
                content += "|--------|-------|--------|\n"

                for metric, data in metrics.items():
                    value = data.get("value", "N/A")
                    status = data.get("status", "⚪")
                    content += f"| {metric} | {value} | {status} |\n"

        super().__init__(content)


class RecommendationsBlock(ChainableBlock):
    """Block for displaying recommendations."""

    def __init__(
        self,
        recommendations: List[str],
        title: str = "Recommendations",
        numbered: bool = True
    ):
        """
        Create recommendations block.

        Args:
            recommendations: List of recommendation strings
            title: Section title
            numbered: Whether to use numbered list
        """
        if not recommendations:
            content = f"\n## 🚀 {title}\n\n_No recommendations available._\n"
        else:
            content = f"\n## 🚀 {title}\n\n"

            if numbered:
                content += "\n".join(f"{i+1}. {r}" for i, r in enumerate(recommendations))
            else:
                content += "\n".join(f"- {r}" for r in recommendations)

            content += "\n"

        super().__init__(content)


class NextStepsBlock(ChainableBlock):
    """Block for displaying next steps with priority."""

    def __init__(
        self,
        steps: List[Dict[str, Any]],
        title: str = "Next Steps"
    ):
        """
        Create next steps block.

        Args:
            steps: List of step dicts with description, priority, effort
            title: Section title
        """
        if not steps:
            content = f"\n## ⏭️ {title}\n\n_All work complete._\n"
        else:
            content = f"\n## ⏭️ {title}\n\n"
            content += "| Step | Priority | Effort |\n"
            content += "|------|----------|--------|\n"

            for step in steps:
                desc = step.get("description", "Unknown")
                priority = step.get("priority", "P2")
                effort = step.get("effort", "N/A")

                # Priority emoji
                priority_emoji = {
                    "P0": "🔴",
                    "P1": "🟡",
                    "P2": "🟢",
                    "P3": "🔵"
                }.get(priority, "⚪")

                content += f"| {desc} | {priority_emoji} {priority} | {effort} |\n"

        super().__init__(content)


class CodeComparisonBlock(ChainableBlock):
    """Block for before/after code comparison."""

    def __init__(
        self,
        before: str,
        after: str,
        language: str = "python",
        title: str = "Code Comparison"
    ):
        """
        Create code comparison block.

        Args:
            before: Before code
            after: After code
            language: Code language for syntax highlighting
            title: Section title
        """
        content = f"\n## {title}\n\n"
        content += "### ❌ Before\n\n"
        content += f"```{language}\n{before}\n```\n\n"
        content += "### ✅ After\n\n"
        content += f"```{language}\n{after}\n```\n"

        super().__init__(content)


class ErrorAnalysisBlock(ChainableBlock):
    """Block for error analysis."""

    def __init__(
        self,
        error_type: str,
        message: str,
        location: str,
        stack_trace: Optional[str] = None,
        title: str = "Error Analysis"
    ):
        """
        Create error analysis block.

        Args:
            error_type: Type of error
            message: Error message
            location: Error location
            stack_trace: Optional stack trace
            title: Section title
        """
        content = f"\n## 🔍 {title}\n\n"
        content += "| Field | Value |\n"
        content += "|-------|-------|\n"
        content += f"| **Type** | {error_type} |\n"
        content += f"| **Message** | {message} |\n"
        content += f"| **Location** | {location} |\n"

        if stack_trace:
            content += "\n### Stack Trace\n\n"
            content += f"```\n{stack_trace}\n```\n"

        super().__init__(content)


# ============================================================================
# BLOCK COMPOSER (FLUENT API)
# ============================================================================


class BlockComposer:
    """
    Fluent API for composing template blocks.

    Usage:
        response = (BlockComposer()
            .add_test_results(tests)
            .add_coverage(coverage)
            .add_recommendations(recs)
            .build())
    """

    def __init__(self):
        self.blocks: List[ChainableBlock] = []

    def add_test_results(
        self,
        tests: List[Dict[str, Any]],
        title: str = "Test Results"
    ) -> 'BlockComposer':
        """Add test results block."""
        if tests:
            self.blocks.append(TestResultsBlock(tests, title))
        return self

    def add_coverage(
        self,
        metrics: Dict[str, float],
        title: str = "Coverage Metrics"
    ) -> 'BlockComposer':
        """Add coverage metrics block."""
        if metrics:
            self.blocks.append(CoverageMetricsBlock(metrics, title))
        return self

    def add_problem_solution(
        self,
        pairs: List[Tuple[str, str]],
        title: str = "Issues & Solutions"
    ) -> 'BlockComposer':
        """Add problem/solution block."""
        if pairs:
            self.blocks.append(ProblemSolutionBlock(pairs, title))
        return self

    def add_validation_checklist(
        self,
        checks: Dict[str, bool],
        title: str = "Validation Results"
    ) -> 'BlockComposer':
        """Add validation checklist block."""
        if checks:
            self.blocks.append(ValidationChecklistBlock(checks, title))
        return self

    def add_metrics_dashboard(
        self,
        metrics: Dict[str, Any],
        title: str = "Metrics Dashboard"
    ) -> 'BlockComposer':
        """Add metrics dashboard block."""
        if metrics:
            self.blocks.append(MetricsDashboardBlock(metrics, title))
        return self

    def add_recommendations(
        self,
        recommendations: List[str],
        title: str = "Recommendations"
    ) -> 'BlockComposer':
        """Add recommendations block."""
        if recommendations:
            self.blocks.append(RecommendationsBlock(recommendations, title))
        return self

    def add_next_steps(
        self,
        steps: List[Dict[str, Any]],
        title: str = "Next Steps"
    ) -> 'BlockComposer':
        """Add next steps block."""
        if steps:
            self.blocks.append(NextStepsBlock(steps, title))
        return self

    def add_code_comparison(
        self,
        before: str,
        after: str,
        language: str = "python",
        title: str = "Code Comparison"
    ) -> 'BlockComposer':
        """Add code comparison block."""
        if before and after:
            self.blocks.append(CodeComparisonBlock(before, after, language, title))
        return self

    def add_error_analysis(
        self,
        error_type: str,
        message: str,
        location: str,
        stack_trace: Optional[str] = None,
        title: str = "Error Analysis"
    ) -> 'BlockComposer':
        """Add error analysis block."""
        self.blocks.append(ErrorAnalysisBlock(error_type, message, location, stack_trace, title))
        return self

    def add_custom(self, block: ChainableBlock) -> 'BlockComposer':
        """Add custom block."""
        self.blocks.append(block)
        return self

    def build(self) -> str:
        """
        Build final response from all blocks.

        Validates zone conflicts before composition.

        Returns:
            Combined response content

        Raises:
            RuntimeError: If zone conflicts detected
        """
        # Validate no zone conflicts
        zones_used: Set[ContentZone] = set()

        for block in self.blocks:
            if block.zone:
                if block.zone in zones_used:
                    raise RuntimeError(
                        f"Content zone conflict: {block.zone.value} used multiple times. "
                        f"BlockComposer detected duplicate semantic content."
                    )
                zones_used.add(block.zone)

        # Compose blocks
        return "\n".join(block.render() for block in self.blocks)


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "ChainableBlock",
    "TestResultsBlock",
    "CoverageMetricsBlock",
    "ProblemSolutionBlock",
    "ValidationChecklistBlock",
    "MetricsDashboardBlock",
    "RecommendationsBlock",
    "NextStepsBlock",
    "CodeComparisonBlock",
    "ErrorAnalysisBlock",
    "BlockComposer",
]

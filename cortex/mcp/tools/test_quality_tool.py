"""
CORTEX MCP Tool: cortex_score_tests (Phase 07b)

Exposes TestQualityGate scoring via MCP so any onboarded production
repository can score its own test suite using the 7-step algorithm
from test-quality.txt.

Input:  target_path — file or directory to score
Output: per-file scores, KEEP/REVIEW/DELETE summary, golden test
        identification, anti-tests list (refused low-value tests)

Authority: test-quality.txt | CORE-011 | CORE-012
AC-ID: AC-PHASE-07B-TEST-QUALITY-GATE-001
Author: Asif Hussain
Date: 2026-02-20
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.mcp.mcp_tool_base import (
    Tool,
    ToolCategory,
    ToolDefinition,
    ToolParameter,
    ToolResult,
)
from cortex.testing.quality_gate import DELETE, KEEP, REVIEW, TestQualityGate


class CortexScoreTests(Tool):
    """MCP tool: score test files using the CORTEX quality gate.

    Implements the 7-step algorithm from test-quality.txt and returns
    a structured report with per-file scores, summary table, golden test
    identification, and anti-tests list.
    """

    _PARAMETERS: List[ToolParameter] = [
        ToolParameter(
            name="target_path",
            type="string",
            description="File or directory path to score (absolute or relative to workspace root)",
            required=True,
        ),
        ToolParameter(
            name="min_score",
            type="integer",
            description="Minimum acceptable quality score 0–9 (default: 7 per test-quality.txt)",
            required=False,
        ),
        ToolParameter(
            name="report_format",
            type="string",
            description="Output format: 'summary' | 'detailed' | 'json' (default: summary)",
            required=False,
            enum=["summary", "detailed", "json"],
        ),
        ToolParameter(
            name="include_anti_tests",
            type="boolean",
            description="Include list of refused low-value tests in output (default: true)",
            required=False,
        ),
    ]

    @property
    def definition(self) -> ToolDefinition:
        """MCP-compliant tool definition."""
        return ToolDefinition(
            name="cortex_score_tests",
            description=(
                "Score test files using the CORTEX 7-step quality gate algorithm "
                "(test-quality.txt). Returns per-file scores (0-9), "
                "KEEP/REVIEW/DELETE classification, golden test identification, "
                "and an anti-tests list of refused low-value tests. "
                "Callable from any onboarded production repository via MCP."
            ),
            category=ToolCategory.OPERATIONS,
            parameters=self._PARAMETERS,
        )

    # Convenience accessors (used by tests and MCP dispatcher)
    @property
    def name(self) -> str:
        """Tool name exposed to MCP clients."""
        return self.definition.name

    @property
    def description(self) -> str:
        """Human-readable tool description."""
        return self.definition.description

    @property
    def category(self) -> ToolCategory:
        """Tool category for MCP routing."""
        return self.definition.category

    @property
    def parameters(self) -> List[ToolParameter]:
        """MCP tool parameter schema."""
        return self._PARAMETERS

    def execute(self, params: Optional[Dict[str, Any]] = None, **kwargs: Any) -> ToolResult:
        """Execute test quality scoring.

        Accepts params as a dict (from MCP dispatch) or as keyword args.

        Args:
            params: Dict with target_path, min_score, report_format, include_anti_tests.
            **kwargs: Fallback keyword argument support.

        Returns:
            ToolResult with success=True and data containing the quality report.
        """
        # Merge dict params and kwargs for flexibility
        merged: Dict[str, Any] = {}
        if params:
            merged.update(params)
        merged.update(kwargs)

        target_path_str: str = merged.get("target_path", "")
        min_score: float = float(merged.get("min_score", 7))
        report_format: str = merged.get("report_format", "summary")
        include_anti_tests: bool = merged.get("include_anti_tests", True)

        if not target_path_str:
            return ToolResult(
                success=False,
                error="target_path is required",
            )

        target = Path(target_path_str)
        if not target.exists():
            return ToolResult(
                success=False,
                error=f"Path does not exist: {target_path_str}",
            )

        # Collect test files
        if target.is_file():
            test_files = [target] if target.name.startswith("test_") else []
        else:
            test_files = list(target.rglob("test_*.py"))

        if not test_files:
            return ToolResult(
                success=True,
                data={
                    "summary": {KEEP: 0, REVIEW: 0, DELETE: 0},
                    "files": [],
                    "golden_tests": [],
                    "anti_tests": [],
                    "message": "No test files found in target path",
                },
            )

        gate = TestQualityGate()
        file_results = []
        golden_tests: List[str] = []
        anti_tests: List[Dict[str, Any]] = []
        summary: Dict[str, int] = {KEEP: 0, REVIEW: 0, DELETE: 0}

        for test_file in sorted(test_files):
            result = gate.score_file(test_file)
            summary[result.category] = summary.get(result.category, 0) + 1

            file_entry: Dict[str, Any] = {
                "file": str(test_file),
                "score": result.score,
                "category": result.category,
                "is_golden": result.is_golden,
                "n_tests": result.n_tests,
            }

            if report_format in ("detailed", "json"):
                file_entry["breakdown"] = result.breakdown

            file_results.append(file_entry)

            if result.is_golden:
                golden_tests.append(str(test_file))

            if include_anti_tests and result.category == DELETE:
                anti_tests.append({
                    "file": str(test_file),
                    "score": result.score,
                    "reason": self._anti_test_reason(result.breakdown),
                })

        # Build output
        data: Dict[str, Any] = {
            "summary": {
                "keep": summary.get(KEEP, 0),
                "review": summary.get(REVIEW, 0),
                "delete": summary.get(DELETE, 0),
                "total": len(file_results),
                "signal_density_pct": round(
                    summary.get(KEEP, 0) / len(file_results) * 100, 1
                ) if file_results else 0,
            },
            "golden_tests": golden_tests,
        }

        if report_format != "summary":
            data["files"] = file_results

        if include_anti_tests:
            data["anti_tests"] = anti_tests

        return ToolResult(success=True, data=data)

    @staticmethod
    def _anti_test_reason(breakdown: Dict[str, float]) -> str:
        """Generate human-readable reason for refusing a low-value test.

        Args:
            breakdown: Dimension breakdown dict from ScoreResult.

        Returns:
            Human-readable explanation string.
        """
        reasons = []
        if breakdown.get("impact", 0) == 0:
            reasons.append("no security/reliability/business-invariant signals")
        if breakdown.get("likelihood", 0) == 0:
            reasons.append("no orchestration/integration signals")
        if breakdown.get("maintenance_penalty", 0) < -1:
            reasons.append("high maintenance cost (trivial asserts / mocks / stubs)")
        if breakdown.get("efficiency", 0) == 0:
            reasons.append("low efficiency (<15 lines/test, <2 asserts/test)")
        return "; ".join(reasons) if reasons else "score below gate threshold"


__all__ = ["CortexScoreTests"]

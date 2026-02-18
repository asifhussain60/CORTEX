"""Health Orchestrator MCP Tool — Phase 48 + Phase 49

Exposes Phase 48 HealthOrchestrator and HealthVacuumPipeline via MCP-first
architecture.  Routes through MasterOrchestrator → validates orchestrator_context.

Operations:
- scan:     Run HealthOrchestrator.scan() → write health-issues.yaml
- pipeline: Run full HealthVacuumPipeline (scan + vacuum in one call)
- status:   Query existing health-issues.yaml without rescanning
- classify: (Phase 49) Classify a module path → TestDecision (tier, concerns,
            target_folder, required_markers, coverage_floor) — CORE-055

CORE-028: kebab-case file, snake_case symbols
CORE-008: golden tests in tests/golden/orchestrators/health_vacuum/
CORE-035: single canonical implementation in health_orchestrator.py
CORE-055: Golden Test Tier Contract (Phase 49)

Phase: Phase 48 / Phase 49 — Health-Vacuum + Golden Test Promotion
Author: CORTEX Framework
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools.utilities import validate_orchestrator_context
from cortex.orchestrators.support.health_orchestrator import (
    HealthOrchestrator,
    HealthVacuumPipeline,
    IssueCategory,
)

_DEFAULT_WORKSPACE = Path(__file__).resolve().parents[3]
_DEFAULT_HANDOFF = _DEFAULT_WORKSPACE / "cortex" / "brain" / "vacuum" / "health-issues.yaml"


class CortexHealthOrchestrate(ConsolidatedTool):
    """MCP tool: run Phase 48 HealthOrchestrator to scan CORTEX integrity.

    Scans the repository for screaming-case names, empty files, orphaned
    directories, wrong path references, duplicate content, deprecated markers,
    and invalid markdown placement.  Writes a structured YAML handoff file
    for VacuumExecutor to consume.

    Operations:
        scan     — Run all health checks; write health-issues.yaml
        pipeline — Run full scan → vacuum pipeline autonomously
        status   — Read and return existing health-issues.yaml (no re-scan)
    """

    @property
    def name(self) -> str:
        return "cortex_health_orchestrate"

    @property
    def description(self) -> str:
        return (
            "Run Phase 48 HealthOrchestrator to scan CORTEX repository integrity. "
            "Detects screaming-case files, empty files, orphaned directories, "
            "wrong references, duplicate content, deprecated markers, and invalid "
            "markdown placement.  Writes health-issues.yaml for VacuumExecutor. "
            "Operations: scan | pipeline | status."
        )

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.UTILITIES

    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="operation",
                type="string",
                description="Operation to perform: scan, pipeline, status, or classify",
                required=True,
                enum=["scan", "pipeline", "status", "classify"],
            ),
            ToolParameter(
                name="module_path",
                type="string",
                description=(
                    "[classify only] Absolute or relative path to a Python module. "
                    "Returns TestDecision (tier, concerns, target_folder, "
                    "required_markers, coverage_floor). CORE-055."
                ),
                required=False,
            ),
            ToolParameter(
                name="workspace_root",
                type="string",
                description=(
                    "Absolute path to CORTEX repository root. "
                    "Defaults to the CORTEX project root."
                ),
                required=False,
            ),
            ToolParameter(
                name="handoff_path",
                type="string",
                description=(
                    "Absolute path for health-issues.yaml output/input. "
                    "Defaults to cortex/brain/vacuum/health-issues.yaml."
                ),
                required=False,
            ),
            ToolParameter(
                name="dry_run",
                type="boolean",
                description=(
                    "Dry-run mode: scan and report without writing handoff file "
                    "or executing vacuum operations."
                ),
                required=False,
            ),
            ToolParameter(
                name="autonomous",
                type="boolean",
                description=(
                    "Pipeline autonomous mode: skip interactive review stage. "
                    "Only used when operation=pipeline."
                ),
                required=False,
            ),
            ToolParameter(
                name="orchestrator_context",
                type="object",
                description="MasterOrchestrator routing context (required for all calls).",
                required=True,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["scan", "pipeline", "status", "classify"]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(self, **params: Any) -> ToolResult:
        """Execute health orchestrator operation.

        Args:
            **params: Tool parameters including operation, workspace_root,
                      handoff_path, dry_run, autonomous, orchestrator_context.

        Returns:
            ToolResult with scan summary or pipeline report.
        """
        validate_orchestrator_context(params.get("orchestrator_context"))

        operation: str = params.get("operation", "scan")
        workspace_root: str = params.get("workspace_root", str(_DEFAULT_WORKSPACE))
        handoff_path: str = params.get("handoff_path", str(_DEFAULT_HANDOFF))
        dry_run: bool = bool(params.get("dry_run", False))
        autonomous: bool = bool(params.get("autonomous", True))

        workspace = Path(workspace_root)
        handoff = Path(handoff_path)

        if not workspace.exists():
            return ToolResult(
                success=False,
                data={"error": f"Workspace not found: {workspace_root}"},
                metadata={"operation": operation},
            )

        if operation == "scan":
            return await self._op_scan(workspace, handoff, dry_run)

        if operation == "pipeline":
            return await self._op_pipeline(workspace, handoff, dry_run, autonomous)

        if operation == "status":
            return await self._op_status(handoff)

        if operation == "classify":
            module_path: str = params.get("module_path", "")
            return await self._op_classify(module_path)

        return ToolResult(
            success=False,
            data={"error": f"Unknown operation: {operation}"},
            metadata={"operation": operation},
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _op_scan(
        self,
        workspace: Path,
        handoff: Path,
        dry_run: bool,
    ) -> ToolResult:
        """Run HealthOrchestrator.scan() and optionally write handoff."""
        try:
            orchestrator = HealthOrchestrator(workspace)
            result = orchestrator.scan()

            if not dry_run:
                orchestrator.write_handoff(result, handoff)

            issues_by_category: Dict[str, int] = {}
            for issue in result.issues:
                key = issue.category.value
                issues_by_category[key] = issues_by_category.get(key, 0) + 1

            return ToolResult(
                success=True,
                data={
                    "total_issues": len(result.issues),
                    "files_scanned": result.files_scanned,
                    "issues_by_category": issues_by_category,
                    "handoff_written": not dry_run,
                    "handoff_path": str(handoff) if not dry_run else None,
                    "top_issues": [
                        {
                            "category": i.category.value,
                            "action": i.action,
                            "path": str(i.path),
                            "recommended_name": i.recommended_name,
                        }
                        for i in result.issues[:20]
                    ],
                    "dry_run": dry_run,
                },
                metadata={
                    "operation": "scan",
                    "workspace": str(workspace),
                },
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                success=False,
                data={"error": str(exc)},
                metadata={"operation": "scan"},
            )

    async def _op_pipeline(
        self,
        workspace: Path,
        handoff: Path,
        dry_run: bool,
        autonomous: bool,
    ) -> ToolResult:
        """Run the full HealthVacuumPipeline."""
        try:
            pipeline = HealthVacuumPipeline(
                workspace_root=workspace,
                handoff_path=handoff,
                dry_run=dry_run,
            )
            report = pipeline.run(autonomous=autonomous)

            stage_summaries = [
                {
                    "stage": s.stage,
                    "status": s.status,
                    "details": s.details,
                }
                for s in report.stages
            ]

            return ToolResult(
                success=report.overall_status == "PASS",
                data={
                    "overall_status": report.overall_status,
                    "issues_found": report.issues_found,
                    "operations_planned": report.operations_planned,
                    "operations_executed": report.operations_executed,
                    "operations_failed": report.operations_failed,
                    "stages": stage_summaries,
                    "dry_run": dry_run,
                    "autonomous": autonomous,
                },
                metadata={
                    "operation": "pipeline",
                    "workspace": str(workspace),
                },
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                success=False,
                data={"error": str(exc)},
                metadata={"operation": "pipeline"},
            )

    async def _op_status(self, handoff: Path) -> ToolResult:
        """Read and return existing health-issues.yaml without re-scanning."""
        if not handoff.exists():
            return ToolResult(
                success=True,
                data={
                    "handoff_exists": False,
                    "message": "No pending health-issues.yaml found. Run scan first.",
                },
                metadata={"operation": "status"},
            )

        try:
            with handoff.open() as fh:
                data: Dict[str, Any] = yaml.safe_load(fh) or {}

            issues = data.get("issues", [])
            by_category: Dict[str, int] = {}
            for issue in issues:
                key = issue.get("category", "unknown")
                by_category[key] = by_category.get(key, 0) + 1

            return ToolResult(
                success=True,
                data={
                    "handoff_exists": True,
                    "handoff_path": str(handoff),
                    "generated_at": data.get("generated_at"),
                    "workspace": data.get("workspace"),
                    "total_issues": len(issues),
                    "issues_by_category": by_category,
                    "issues": issues[:20],
                },
                metadata={"operation": "status"},
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                success=False,
                data={"error": f"Failed to read handoff: {exc}"},
                metadata={"operation": "status"},
            )

    async def _op_classify(self, module_path: str) -> ToolResult:
        """Classify a module path using TestClassifierOrchestrator (CORE-055).

        Args:
            module_path: Relative or absolute path to a Python module.

        Returns:
            ToolResult with tier, concerns, target_folder, required_markers,
            and coverage_floor.
        """
        if not module_path:
            return ToolResult(
                success=False,
                data={"error": "module_path is required for operation=classify"},
                metadata={"operation": "classify"},
            )
        try:
            from cortex.orchestrators.support.test_classifier_orchestrator import (
                TestClassifierOrchestrator,
            )
            classifier = TestClassifierOrchestrator()
            decision = classifier.classify(module_path)
            return ToolResult(
                success=True,
                data={
                    "module_path": module_path,
                    "tier": decision.tier.value,
                    "concerns": [c.value for c in decision.concerns],
                    "target_folder": decision.target_folder,
                    "required_markers": decision.required_markers,
                    "coverage_floor": decision.coverage_floor,
                },
                metadata={"operation": "classify", "core_rule": "CORE-055"},
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                success=False,
                data={"error": str(exc)},
                metadata={"operation": "classify"},
            )


__all__ = ["CortexHealthOrchestrate"]

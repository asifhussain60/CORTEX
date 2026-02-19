"""Vacuum Orchestrator MCP Tool — Phase 48 / Phase 50

Exposes Phase 48 VacuumExecutor via MCP-first architecture.
Consumes health-issues.yaml produced by CortexHealthOrchestrate (scan op)
and executes file rename / delete / relocate operations.

Operations:
- execute:  Consume handoff file, run all vacuum operations
- rollback: Restore files from rollback manifest
- preview:  Dry-run — show planned operations without executing
- markdown: Archive stale .md files into .cortex-runtime/archived-docs/

CORE-028: kebab-case file, snake_case symbols
CORE-008: golden tests in tests/golden/orchestrators/health_vacuum/
CORE-035: single canonical VacuumExecutor in health_orchestrator.py

Phase: Phase 48 / Phase 50 — Health-Vacuum Integrity Pipeline
Author: CORTEX Framework
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context
from cortex.orchestrators.support.health_orchestrator import VacuumExecutor

_DEFAULT_WORKSPACE = Path(__file__).resolve().parents[3]
_DEFAULT_HANDOFF = _DEFAULT_WORKSPACE / "cortex" / "brain" / "vacuum" / "health-issues.yaml"
_DEFAULT_MANIFEST = _DEFAULT_WORKSPACE / "cortex" / "brain" / "vacuum" / "rollback-manifest.json"


class CortexVacuumOrchestrate(ConsolidatedTool):
    """MCP tool: run Phase 48 VacuumExecutor to remediate CORTEX integrity issues.

    Consumes the health-issues.yaml handoff file produced by
    CortexHealthOrchestrate (scan operation) and executes the planned
    file operations: rename screaming-case → kebab-case, delete empty
    files/dirs, relocate misplaced production files, and delete the
    handoff file on successful teardown.

    Operations:
        execute  — Run all vacuum operations from handoff file
        rollback — Restore state from rollback-manifest.json
        preview  — Dry-run: show planned ops without executing
        markdown — Archive stale .md files into .cortex-runtime/archived-docs/
    """

    @property
    def name(self) -> str:
        return "cortex_vacuum_orchestrate"

    @property
    def description(self) -> str:
        return (
            "Run Phase 48 VacuumExecutor to remediate CORTEX repository issues. "
            "Consumes health-issues.yaml from HealthOrchestrator scan and executes "
            "rename (screaming→kebab), delete, and relocate operations. "
            "Supports rollback via manifest file. "
            "Operations: execute | rollback | preview."
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
                description="Operation to perform: execute, rollback, preview, or markdown",
                required=True,
                enum=["execute", "rollback", "preview", "markdown"],
            ),
            ToolParameter(
                name="handoff_path",
                type="string",
                description=(
                    "Absolute path to health-issues.yaml. "
                    "Defaults to cortex/brain/vacuum/health-issues.yaml."
                ),
                required=False,
            ),
            ToolParameter(
                name="manifest_path",
                type="string",
                description=(
                    "Absolute path for rollback-manifest.json. "
                    "Defaults to cortex/brain/vacuum/rollback-manifest.json. "
                    "Required when operation=rollback."
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
                name="orchestrator_context",
                type="object",
                description="MasterOrchestrator routing context (required for all calls).",
                required=True,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        return ["execute", "rollback", "preview", "markdown"]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def execute(self, **params: Any) -> ToolResult:
        """Execute vacuum orchestrator operation.

        Args:
            **params: Tool parameters including operation, handoff_path,
                      manifest_path, workspace_root, orchestrator_context.

        Returns:
            ToolResult with operation results or rollback status.
        """
        validate_orchestrator_context(params.get("orchestrator_context"))

        operation: str = params.get("operation", "execute")
        handoff_path: str = params.get("handoff_path", str(_DEFAULT_HANDOFF))
        manifest_path: str = params.get("manifest_path", str(_DEFAULT_MANIFEST))
        workspace_root: str = params.get("workspace_root", str(_DEFAULT_WORKSPACE))

        handoff = Path(handoff_path)
        manifest = Path(manifest_path)
        workspace = Path(workspace_root)

        if operation == "execute":
            return await self._op_execute(workspace, handoff, manifest, dry_run=False)

        if operation == "preview":
            return await self._op_execute(workspace, handoff, manifest, dry_run=True)

        if operation == "rollback":
            return await self._op_rollback(workspace, manifest)

        if operation == "markdown":
            return await self._op_markdown_vacuum(workspace)

        return ToolResult(
            success=False,
            data={"error": f"Unknown operation: {operation}"},
            metadata={"operation": operation},
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    async def _op_execute(
        self,
        workspace: Path,
        handoff: Path,
        manifest: Path,
        dry_run: bool,
    ) -> ToolResult:
        """Execute or preview vacuum operations from handoff file."""
        if not handoff.exists():
            return ToolResult(
                success=False,
                data={
                    "error": (
                        f"Handoff file not found: {handoff}. "
                        "Run cortex_health_orchestrate(operation='scan') first."
                    )
                },
                metadata={"operation": "preview" if dry_run else "execute"},
            )

        try:
            executor = VacuumExecutor(workspace_root=workspace, dry_run=dry_run)
            ops = executor.execute_from_handoff(handoff)

            if not dry_run and manifest.parent.exists():
                executor.save_rollback_manifest(manifest)

            succeeded = [o for o in ops if o.success]
            failed = [o for o in ops if not o.success]

            return ToolResult(
                success=len(failed) == 0,
                data={
                    "operations_planned": len(ops),
                    "operations_executed": len(succeeded) if not dry_run else 0,
                    "operations_failed": len(failed),
                    "dry_run": dry_run,
                    "manifest_saved": (not dry_run and manifest.exists()),
                    "manifest_path": str(manifest) if not dry_run else None,
                    "results": [
                        {
                            "operation": o.operation,
                            "source": str(o.source),
                            "destination": str(o.destination) if o.destination else None,
                            "success": o.success,
                            "message": o.message,
                        }
                        for o in ops[:50]
                    ],
                    "failures": [
                        {
                            "operation": o.operation,
                            "source": str(o.source),
                            "message": o.message,
                        }
                        for o in failed
                    ],
                },
                metadata={
                    "operation": "preview" if dry_run else "execute",
                    "handoff": str(handoff),
                },
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                success=False,
                data={"error": str(exc)},
                metadata={"operation": "preview" if dry_run else "execute"},
            )

    async def _op_rollback(self, workspace: Path, manifest: Path) -> ToolResult:
        """Restore files from rollback manifest."""
        if not manifest.exists():
            return ToolResult(
                success=False,
                data={
                    "error": (
                        f"Rollback manifest not found: {manifest}. "
                        "No execute operation has been performed, or manifest was already deleted."
                    )
                },
                metadata={"operation": "rollback"},
            )

        try:
            executor = VacuumExecutor(workspace_root=workspace, dry_run=False)
            restored = executor.rollback(manifest)

            return ToolResult(
                success=True,
                data={
                    "restored_count": len(restored),
                    "restored": [
                        {
                            "destination": str(r.destination),
                            "source": str(r.source),
                            "success": r.success,
                            "message": r.message,
                        }
                        for r in restored[:50]
                    ],
                    "manifest_deleted": not manifest.exists(),
                },
                metadata={
                    "operation": "rollback",
                    "manifest": str(manifest),
                },
            )
        except Exception as exc:  # noqa: BLE001
            return ToolResult(
                success=False,
                data={"error": str(exc)},
                metadata={"operation": "rollback"},
            )


    async def _op_markdown_vacuum(self, workspace: Path) -> ToolResult:
        """Archive stale markdown files using CORTEX vacuum conventions.

        Scans for .md files in non-canonical locations and archives them
        under .cortex-runtime/archived-docs/ following CORE-002 (no bash
        generation of markdown files) and cortex_vacuum cleanup rules.

        Args:
            workspace: Repository root path.

        Returns:
            ToolResult with count of archived markdown files.

        AC: GP50-009 — markdown operation absorbed into CortexVacuumOrchestrate
        """
        archive_root = workspace / ".cortex-runtime" / "archived-docs"
        archive_root.mkdir(parents=True, exist_ok=True)

        # Protected locations — canonical docs live here
        protected_prefixes = (
            "cortex-docs",
            "docs",
            ".github",
            "README",
        )

        archived: list[dict[str, str]] = []
        errors: list[str] = []

        for md_file in workspace.rglob("*.md"):
            try:
                rel = md_file.relative_to(workspace)
            except ValueError:
                continue

            rel_str = str(rel)

            # Skip protected locations
            if any(rel_str.startswith(p) for p in protected_prefixes):
                continue

            # Skip already-archived files
            if ".cortex-runtime" in rel_str:
                continue

            # Archive: move to .cortex-runtime/archived-docs/ preserving structure
            dest = archive_root / rel
            try:
                dest.parent.mkdir(parents=True, exist_ok=True)
                if not dest.exists():
                    md_file.rename(dest)
                    archived.append({"source": rel_str, "dest": str(dest.relative_to(workspace))})
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{rel_str}: {exc}")

        return ToolResult(
            success=len(errors) == 0,
            data={
                "archived": archived,
                "archived_count": len(archived),
                "errors": errors,
                "archive_root": str(archive_root.relative_to(workspace)),
            },
            metadata={"operation": "markdown"},
        )


__all__ = ["CortexVacuumOrchestrate"]

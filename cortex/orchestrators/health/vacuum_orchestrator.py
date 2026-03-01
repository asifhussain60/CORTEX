"""VacuumOrchestrator — Standalone + Companion Remediation Engine

Single canonical vacuum orchestrator with DUAL operating modes:

**STANDALONE MODE** — ``VacuumOrchestrator(root).run()``:
    Performs its own lightweight FileContext scan and executes
    all cleanup operations without requiring a prior health scan.

**COMPANION MODE** — ``VacuumOrchestrator(root).consume(handoff)``:
    Reads ``health-issues.yaml`` produced by HealthOrchestrator.scan()
    and executes all prescribed remediation operations.

All operations record rollback entries.  Dry-run mode supported.

Phase: PHASE-51
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-028 (naming), CORE-035 (single canonical)
"""

from __future__ import annotations

import json
import logging
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .constants import (
    ALLOWED_MARKDOWN_PREFIXES,
    ARCHIVE_DIR,
    LEGACY_ROOT_FOLDERS_RELOCATION,
    PROTECTED_DIRS,
    PROTECTED_FILES,
    PYTHON_EXTENSIONS,
)
from .file_context import FileContext
from .models import IssueFile, IssueSeverity, OperationResult, ScanResult, VacuumReport
from .naming import classify_naming_violation, is_screaming, to_kebab_case, to_snake_case
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin

# GAP-57-08: Wire tier1_learned cleaners (Phase 57-f)
try:
    from cortex.intelligence.memory.tier1_learned.orchestrators.cleaners.root_artifacts import (
        RootArtifactsCleaner,
    )
    _tier1_root_artifacts = RootArtifactsCleaner
except ImportError:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "Optional cortex dependency unavailable: "
        "cortex.intelligence.memory.tier1_learned.orchestrators.cleaners.root_artifacts"
        " — feature degraded"
    )
    _tier1_root_artifacts = None  # type: ignore[assignment]

try:
    from cortex.intelligence.memory.tier1_learned.orchestrators.cleaners.markdown_sprawl import (
        MarkdownSprawlCleaner,
    )
    _tier1_markdown_sprawl = MarkdownSprawlCleaner
except ImportError:
    import logging as _logging
    _logging.getLogger(__name__).warning(
        "Optional cortex dependency unavailable: "
        "cortex.intelligence.memory.tier1_learned.orchestrators.cleaners.markdown_sprawl"
        " — feature degraded"
    )
    _tier1_markdown_sprawl = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class VacuumOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin, WorkflowTemplateMixin):
    """Standalone + companion remediation engine.

    Usage (standalone)::

        vac = VacuumOrchestrator(Path("/project"))
        report = vac.run()          # quick-scan + execute
        report = vac.run(dry_run=True)  # preview only

    Usage (companion)::

        vac = VacuumOrchestrator(Path("/project"))
        report = vac.consume(Path(".cortex-runtime/health-issues.yaml"))

    Attributes:
        workspace_root: Absolute path of the workspace.
    """

    # Phase 90 — Gateway opt-in pilot: VacuumOrchestrator is the second maintenance
    # orchestrator to route all execution through WorkflowGateway.
    # Safe: vacuum has dry_run=True as default guard; gateway adds template traceability.
    PHASE90_GATEWAY_ENABLED: bool = True

    def __init__(self, workspace_root: Path) -> None:
        """Initialise the vacuum orchestrator.

        Args:
            workspace_root: Root of the workspace to clean.
        """
        self.workspace_root = workspace_root
        self._rollback_log: List[Dict[str, Any]] = []

    def get_recommended_template(self) -> str:
        """Return the canonical workflow template for VACUUM operations.

        Phase 90: WorkflowGateway uses this to resolve the template ID
        before any vacuum execution begins.

        Returns:
            Template ID: 'maintenance/vacuum-workflow'
        """
        return "maintenance/vacuum-workflow"

    # ─────────────────────────────────────────────────────────────────────
    # STANDALONE PUBLIC API
    # ─────────────────────────────────────────────────────────────────────

    @enforce_gateway
    def execute_operation(self, operation_name: str, parameters: dict) -> Any:
        """Gateway entry point — routes VACUUM mode through WorkflowGateway (Phase 90b)."""
        dry_run: bool = parameters.get("dry_run", False)
        return self.run(dry_run=dry_run)

    def run(self, *, dry_run: bool = False) -> VacuumReport:
        """Standalone mode — quick-scan + execute all cleanup ops.

        Args:
            dry_run: If ``True``, plan operations without executing.

        Returns:
            :class:`VacuumReport` with all operation outcomes.
        """
        report = VacuumReport(dry_run=dry_run)
        import time as _time
        _ac_id = f"AC-VACUUM-{int(_time.time() * 1000)}"
        # AC_START: {_ac_id}
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="vacuum_run")
        ctx = FileContext.build(self.workspace_root)

        # Naming fixes
        for op in self._plan_naming_fixes(ctx):
            result = self._execute_op(op, dry_run=dry_run)
            report.operations.append(result)

        # Root cleanup
        for op in self._plan_root_cleanup(ctx):
            result = self._execute_op(op, dry_run=dry_run)
            report.operations.append(result)

        # Empty files
        for op in self._plan_empty_cleanup(ctx):
            result = self._execute_op(op, dry_run=dry_run)
            report.operations.append(result)

        # Orphaned dirs
        for op in self._plan_orphan_cleanup(ctx):
            result = self._execute_op(op, dry_run=dry_run)
            report.operations.append(result)

        # Markdown archival
        for op in self._plan_markdown_archive(ctx):
            result = self._execute_op(op, dry_run=dry_run)
            report.operations.append(result)

        # Digested chat-* file cleanup
        for result in self.run_digest_cleanup(dry_run=dry_run):
            report.operations.append(result)

        report.recount()
        # AC_COMPLETE: {_ac_id} ✅
        return report

    def run_root_cleanup(self, *, dry_run: bool = False) -> List[OperationResult]:
        """Standalone: relocate root files to subfolders.

        Args:
            dry_run: Preview only.

        Returns:
            List of operation results.
        """
        ctx = FileContext.build(self.workspace_root)
        results = []
        for op in self._plan_root_cleanup(ctx):
            results.append(self._execute_op(op, dry_run=dry_run))
        return results

    def run_naming_fix(self, *, dry_run: bool = False) -> List[OperationResult]:
        """Standalone: enforce naming conventions across workspace.

        Args:
            dry_run: Preview only.

        Returns:
            List of operation results.
        """
        ctx = FileContext.build(self.workspace_root)
        results = []
        for op in self._plan_naming_fixes(ctx):
            results.append(self._execute_op(op, dry_run=dry_run))
        return results

    def run_markdown_archive(self, *, dry_run: bool = False) -> List[OperationResult]:
        """Standalone: archive stale markdown files.

        Args:
            dry_run: Preview only.

        Returns:
            List of operation results.
        """
        ctx = FileContext.build(self.workspace_root)
        results = []
        for op in self._plan_markdown_archive(ctx):
            results.append(self._execute_op(op, dry_run=dry_run))
        return results

    def run_legacy_folder_relocation(self, *, dry_run: bool = False) -> List[OperationResult]:
        """Relocate legacy root-level folders to their proper locations.

        Handles relocation of misplaced directories at the workspace root:
        - ``cortex_brain/`` → ``.cortex-runtime/state/cortex_brain/`` (runtime state)
        - ``cortex-sts/`` → ``_workspaces/cortex-sts/`` (demo material)

        Args:
            dry_run: When ``True``, plan operations but do not execute them.

        Returns:
            List of :class:`OperationResult` describing each planned or executed action.
        """
        results: List[OperationResult] = []

        for source_name, dest_rel in LEGACY_ROOT_FOLDERS_RELOCATION.items():
            source = self.workspace_root / source_name
            dest = self.workspace_root / dest_rel

            if not source.exists():
                continue

            if dest.exists():
                logger.warning(
                    "Skipping relocation of %s — destination %s already exists",
                    source, dest,
                )
                results.append(OperationResult(
                    op_type="relocate_dir", source=source, success=False,
                    error=f"Destination already exists: {dest}",
                ))
                continue

            if dry_run:
                results.append(OperationResult(
                    op_type="relocate_dir", source=source, destination=dest,
                    success=True, dry_run=True,
                ))
                logger.info("[DRY-RUN] Would relocate %s → %s", source, dest)
            else:
                results.append(self.relocate_directory(source, dest))

        return results

    def run_runtime_cleanup(self, *, dry_run: bool = False) -> List[OperationResult]:
        """Delete stale files and empty directories inside ``.cortex-runtime/``.

        Targets:
        - ``*.log`` files at ``.cortex-runtime/`` root (``setup.log``, ``mcp-self-healing.log``)
        - ``reports/*.json`` — stale readiness snapshots
        - ``sessions/*.md`` — stale session markdown (CORE-002)
        - ``archived-docs/**`` — all files (already processed artefacts)
        - Empty subdirectories that accumulate over time (``sweeps/``, ``telemetry/``,
          ``vacuum_cache/``, ``locks/``)

        Preserved (never touched):
        - ``traces/*.db``, ``wiring/*.db``, ``intelligence/*.db``, ``audit.db*``
          — live SQLite audit trail (CORE persistence target)
        - ``health_cache/*.json`` — active agent cache
        - ``setup-mcp.py`` — MCP configuration script

        Args:
            dry_run: When ``True``, plan operations but do not execute them.

        Returns:
            List of :class:`OperationResult` describing each planned or executed action.
        """
        runtime_root = self.workspace_root / ".cortex-runtime"
        if not runtime_root.exists():
            return []

        # Files that must never be deleted regardless of extension
        _KEEP_FILES: frozenset[str] = frozenset({
            "setup-mcp.py",
            "audit.db",
            "audit.db-shm",
            "audit.db-wal",
        })

        # Subdirectories whose files are always preserved
        _KEEP_SUBDIRS: frozenset[str] = frozenset({
            "traces",
            "wiring",
            "intelligence",
            "health_cache",
        })

        results: List[OperationResult] = []

        # ── 1. Root-level *.log files ──────────────────────────────────────
        for log_file in runtime_root.glob("*.log"):
            if log_file.name in _KEEP_FILES:
                continue
            if dry_run:
                results.append(OperationResult(op_type="delete", source=log_file, success=True, dry_run=True))
            else:
                results.append(self.delete_file(log_file))

        # ── 2. reports/*.json — stale readiness snapshots ─────────────────
        reports_dir = runtime_root / "reports"
        if reports_dir.exists():
            for report_file in reports_dir.glob("*.json"):
                if dry_run:
                    results.append(OperationResult(op_type="delete", source=report_file, success=True, dry_run=True))
                else:
                    results.append(self.delete_file(report_file))

        # ── 3. sessions/*.md — stale session markdown ──────────────────────
        sessions_dir = runtime_root / "sessions"
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.md"):
                if dry_run:
                    results.append(OperationResult(op_type="delete", source=session_file, success=True, dry_run=True))
                else:
                    results.append(self.delete_file(session_file))

        # ── 4. archived-docs/** — processed archive artefacts ─────────────
        archived_dir = runtime_root / "archived-docs"
        if archived_dir.exists():
            for artefact in sorted(archived_dir.rglob("*")):
                if artefact.is_file():
                    if dry_run:
                        results.append(OperationResult(op_type="delete", source=artefact, success=True, dry_run=True))
                    else:
                        results.append(self.delete_file(artefact))

        # ── 5. Empty subdirectories (leaf → parent order) ──────────────────
        # Collect all subdirs, skip protected ones, remove empty ones bottom-up
        all_subdirs = sorted(
            (d for d in runtime_root.rglob("*") if d.is_dir()),
            key=lambda d: len(d.parts),
            reverse=True,  # deepest first → safe bottom-up removal
        )
        for subdir in all_subdirs:
            try:
                top_level_name = subdir.relative_to(runtime_root).parts[0]
            except (ValueError, IndexError):
                continue
            if top_level_name in _KEEP_SUBDIRS:
                continue
            # Only remove if empty right now (previous iterations may have cleared contents)
            try:
                if not any(subdir.iterdir()):
                    if dry_run:
                        results.append(OperationResult(op_type="rmdir", source=subdir, success=True, dry_run=True))
                    else:
                        results.append(self.delete_directory(subdir))
            except OSError:
                pass

        return results

    def run_digest_cleanup(self, *, dry_run: bool = False) -> List[OperationResult]:
        """Delete stale digested ``chat-*`` files across the workspace.

        Recursively finds all files whose name starts with ``chat-`` and
        deletes them, **except** files inside protected directories
        (``_workspaces``, ``.github``, ``cortex-docs``, ``cortex-registry``,
        etc.) which are preserved.

        Targets:
        - ``cortex/intelligence/state/state/digests/chat-*.json``
        - Any ``chat-*`` files at the workspace root or elsewhere in the tree

        Preserved (never touched):
        - ``_workspaces/**/chat-*`` — user workspace chat sessions
        - ``.github/**/chat-*`` — legitimate templates (e.g. ``chat-vs-terminal-guide.md``)
        - Any ``chat-*`` inside other PROTECTED_DIRS

        Args:
            dry_run: When ``True``, plan operations but do not execute them.

        Returns:
            List of :class:`OperationResult` describing each planned or executed action.
        """
        results: List[OperationResult] = []

        for chat_file in sorted(self.workspace_root.rglob("chat-*")):
            if not chat_file.is_file():
                continue

            # Skip files inside protected directories
            try:
                rel = chat_file.relative_to(self.workspace_root)
                if rel.parts and rel.parts[0] in PROTECTED_DIRS:
                    continue
            except ValueError:
                continue

            if dry_run:
                results.append(OperationResult(
                    op_type="delete", source=chat_file, success=True, dry_run=True,
                ))
            else:
                results.append(self.delete_file(chat_file))

        return results

    def run_empty_cleanup(self, *, dry_run: bool = False) -> List[OperationResult]:
        """Standalone: delete empty files and orphaned dirs.

        Args:
            dry_run: Preview only.

        Returns:
            List of operation results.
        """
        ctx = FileContext.build(self.workspace_root)
        results = []
        for op in self._plan_empty_cleanup(ctx):
            results.append(self._execute_op(op, dry_run=dry_run))
        for op in self._plan_orphan_cleanup(ctx):
            results.append(self._execute_op(op, dry_run=dry_run))
        return results

    # ─────────────────────────────────────────────────────────────────────
    # COMPANION PUBLIC API
    # ─────────────────────────────────────────────────────────────────────

    def consume(self, handoff_path: Path) -> VacuumReport:
        """Companion mode — consume health-issues.yaml and remediate.

        Args:
            handoff_path: Path to the handoff YAML written by
                :meth:`HealthOrchestrator.write_handoff`.

        Returns:
            :class:`VacuumReport` with all operation outcomes.
        """
        data = yaml.safe_load(handoff_path.read_text())
        issues = data.get("issues", [])

        report = VacuumReport()
        for issue in issues:
            check_id = issue.get("check_id", "")
            path = self.workspace_root / issue.get("path", "")
            suggested = issue.get("suggested_fix", "")

            if check_id == "H-001":
                # Screaming rename
                new_name = to_kebab_case(path.name)
                report.operations.append(self.rename_file(path, new_name))
            elif check_id == "H-002":
                # Empty file delete
                report.operations.append(self.delete_file(path))
            elif check_id == "H-003":
                # Orphaned dir
                report.operations.append(self.delete_directory(path))
            elif check_id == "H-007":
                # Markdown archive
                dest = self.workspace_root / ARCHIVE_DIR
                report.operations.append(self.relocate_file(path, dest))
            elif check_id == "H-008":
                # Naming fix
                violation = classify_naming_violation(path.name)
                if violation:
                    report.operations.append(
                        self.rename_file(path, violation.suggested_name)
                    )
            elif check_id == "H-009":
                # Root violation
                dest = self.workspace_root / "misc"
                report.operations.append(self.relocate_file(path, dest))

        report.recount()
        return report

    def execute_from_scan_result(self, scan_result: ScanResult) -> VacuumReport:
        """Direct in-memory handoff from HealthOrchestrator (no YAML).

        Args:
            scan_result: ScanResult from :meth:`HealthOrchestrator.scan`.

        Returns:
            :class:`VacuumReport`.
        """
        report = VacuumReport()
        for issue in scan_result.issues:
            path = self.workspace_root / issue.path
            if issue.check_id == "H-001":
                new_name = to_kebab_case(path.name)
                report.operations.append(self.rename_file(path, new_name))
            elif issue.check_id == "H-002":
                report.operations.append(self.delete_file(path))
            elif issue.check_id == "H-003":
                report.operations.append(self.delete_directory(path))
            elif issue.check_id == "H-007":
                dest = self.workspace_root / ARCHIVE_DIR
                report.operations.append(self.relocate_file(path, dest))
            elif issue.check_id == "H-008":
                violation = classify_naming_violation(path.name)
                if violation:
                    report.operations.append(
                        self.rename_file(path, violation.suggested_name)
                    )
            elif issue.check_id == "H-009":
                dest = self.workspace_root / "misc"
                report.operations.append(self.relocate_file(path, dest))
        report.recount()
        return report

    # ─────────────────────────────────────────────────────────────────────
    # SHARED OPERATIONS (used by both modes)
    # ─────────────────────────────────────────────────────────────────────

    def rename_file(self, source: Path, new_name: str) -> OperationResult:
        """Rename a file atomically (two-step for macOS APFS).

        Args:
            source: Current path.
            new_name: New filename (not full path).

        Returns:
            :class:`OperationResult`.
        """
        destination = source.parent / new_name
        try:
            if not source.exists():
                return OperationResult(
                    op_type="rename", source=source, success=False,
                    error=f"Source does not exist: {source}",
                )
            # Two-step rename for case-insensitive filesystems (macOS APFS)
            tmp = source.parent / f".tmp-{uuid.uuid4().hex[:8]}-{new_name}"
            source.rename(tmp)
            tmp.rename(destination)
            self._rollback_log.append({
                "op": "rename",
                "from": str(destination),
                "to": str(source),
            })
            return OperationResult(
                op_type="rename", source=source, destination=destination, success=True,
            )
        except OSError as exc:
            return OperationResult(
                op_type="rename", source=source, success=False, error=str(exc),
            )

    def delete_file(self, target: Path) -> OperationResult:
        """Delete a file, recording its content for rollback.

        Args:
            target: File to delete.

        Returns:
            :class:`OperationResult`.
        """
        try:
            if not target.exists():
                return OperationResult(
                    op_type="delete", source=target, success=False,
                    error=f"Does not exist: {target}",
                )
            content = target.read_bytes()
            target.unlink()
            self._rollback_log.append({
                "op": "delete",
                "path": str(target),
                "content_b64": content.hex(),
            })
            return OperationResult(op_type="delete", source=target, success=True)
        except OSError as exc:
            return OperationResult(
                op_type="delete", source=target, success=False, error=str(exc),
            )

    def delete_directory(self, target: Path) -> OperationResult:
        """Remove an empty directory.

        Args:
            target: Directory to remove.

        Returns:
            :class:`OperationResult`.
        """
        try:
            if not target.exists():
                return OperationResult(
                    op_type="rmdir", source=target, success=False,
                    error=f"Does not exist: {target}",
                )
            target.rmdir()
            self._rollback_log.append({"op": "rmdir", "path": str(target)})
            return OperationResult(op_type="rmdir", source=target, success=True)
        except OSError as exc:
            return OperationResult(
                op_type="rmdir", source=target, success=False, error=str(exc),
            )

    def delete_directory_tree(self, target: Path) -> OperationResult:
        """Remove a directory tree recursively.

        Args:
            target: Directory to remove.

        Returns:
            :class:`OperationResult`.
        """
        try:
            if not target.exists():
                return OperationResult(
                    op_type="rmtree", source=target, success=False,
                    error=f"Does not exist: {target}",
                )
            shutil.rmtree(target)
            self._rollback_log.append({"op": "rmtree", "path": str(target)})
            return OperationResult(op_type="rmtree", source=target, success=True)
        except OSError as exc:
            return OperationResult(
                op_type="rmtree", source=target, success=False, error=str(exc),
            )

    def relocate_file(self, source: Path, dest_dir: Path) -> OperationResult:
        """Move a file to a different directory.

        Args:
            source: File to move.
            dest_dir: Destination directory (created if needed).

        Returns:
            :class:`OperationResult`.
        """
        try:
            if not source.exists():
                return OperationResult(
                    op_type="relocate", source=source, success=False,
                    error=f"Source does not exist: {source}",
                )
            dest_dir.mkdir(parents=True, exist_ok=True)
            destination = dest_dir / source.name
            shutil.move(str(source), str(destination))
            self._rollback_log.append({
                "op": "relocate",
                "from": str(destination),
                "to": str(source),
            })
            return OperationResult(
                op_type="relocate", source=source, destination=destination,
                success=True,
            )
        except OSError as exc:
            return OperationResult(
                op_type="relocate", source=source, success=False, error=str(exc),
            )

    def relocate_directory(self, source: Path, dest: Path) -> OperationResult:
        """Move an entire directory to a new location.

        Args:
            source: Directory to move.
            dest: Destination path (full path including new directory name).

        Returns:
            :class:`OperationResult`.
        """
        try:
            if not source.exists():
                return OperationResult(
                    op_type="relocate_dir", source=source, success=False,
                    error=f"Source directory does not exist: {source}",
                )
            if not source.is_dir():
                return OperationResult(
                    op_type="relocate_dir", source=source, success=False,
                    error=f"Source is not a directory: {source}",
                )
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(dest))
            self._rollback_log.append({
                "op": "relocate_dir",
                "from": str(dest),
                "to": str(source),
            })
            logger.info("Relocated directory %s → %s", source, dest)
            return OperationResult(
                op_type="relocate_dir", source=source, destination=dest,
                success=True,
            )
        except OSError as exc:
            return OperationResult(
                op_type="relocate_dir", source=source, success=False, error=str(exc),
            )

    # ─────────────────────────────────────────────────────────────────────
    # ROLLBACK & REPORTING
    # ─────────────────────────────────────────────────────────────────────

    def save_rollback_manifest(self, path: Path) -> None:
        """Persist the rollback log to a JSON manifest.

        Args:
            path: Destination file path.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._rollback_log, indent=2))
        logger.info("Rollback manifest saved to %s", path)

    def rollback(self, manifest_path: Path) -> None:
        """Reverse operations recorded in a rollback manifest.

        Args:
            manifest_path: Path to the JSON manifest.
        """
        entries = json.loads(manifest_path.read_text())
        for entry in reversed(entries):
            op = entry["op"]
            try:
                if op == "rename":
                    src = Path(entry["from"])
                    dst = Path(entry["to"])
                    if src.exists():
                        src.rename(dst)
                elif op in ("relocate", "relocate_dir"):
                    src = Path(entry["from"])
                    dst = Path(entry["to"])
                    if src.exists():
                        dst.parent.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(dst))
                elif op == "delete":
                    path = Path(entry["path"])
                    content = bytes.fromhex(entry["content_b64"])
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(content)
                elif op == "rmdir":
                    Path(entry["path"]).mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                logger.warning("Rollback failed for %s: %s", entry, exc)

    def get_report(self) -> VacuumReport:
        """Return a report summarising rollback-log operations."""
        report = VacuumReport()
        for entry in self._rollback_log:
            report.operations.append(
                OperationResult(
                    op_type=entry["op"],
                    source=Path(entry.get("path", entry.get("from", ""))),
                    success=True,
                )
            )
        report.recount()
        return report

    # ─────────────────────────────────────────────────────────────────────
    # INTERNAL PLANNERS
    # ─────────────────────────────────────────────────────────────────────

    def _plan_naming_fixes(
        self, ctx: FileContext
    ) -> List[Dict[str, Any]]:
        """Plan naming-convention fixes.

        Skips files inside PROTECTED_DIRS (e.g. ``_workspaces``, ``.github``,
        ``cortex-sts``) where non-standard naming is intentional.
        """
        ops: List[Dict[str, Any]] = []
        exempt = {"__init__.py", "__main__.py", "conftest.py", "Makefile",
                  "Dockerfile", "Pipfile", ".gitignore", ".gitattributes",
                  ".editorconfig", ".dockerignore", ".pre-commit-config.yaml"}
        for f in ctx.all_files:
            if f.name in exempt:
                continue
            # Never rename inside protected directories
            try:
                rel = f.relative_to(self.workspace_root)
                if rel.parts and rel.parts[0] in PROTECTED_DIRS:
                    continue
            except ValueError:
                pass
            violation = classify_naming_violation(f.name)
            if violation:
                ops.append({
                    "type": "rename",
                    "source": f,
                    "new_name": violation.suggested_name,
                })
        return ops

    def _plan_root_cleanup(
        self, ctx: FileContext
    ) -> List[Dict[str, Any]]:
        """Plan root-file relocations."""
        ops: List[Dict[str, Any]] = []
        for f in ctx.all_files:
            if f.parent != self.workspace_root:
                continue
            if f.name in PROTECTED_FILES:
                continue
            if f.suffix == ".md":
                stem = f.stem.upper()
                if any(stem.startswith(p) for p in ALLOWED_MARKDOWN_PREFIXES):
                    continue
            if f.name.startswith("."):
                continue
            ops.append({
                "type": "relocate",
                "source": f,
                "dest_dir": self.workspace_root / "misc",
            })
        return ops

    def _plan_empty_cleanup(
        self, ctx: FileContext
    ) -> List[Dict[str, Any]]:
        """Plan empty-file deletions.

        Skips files inside PROTECTED_DIRS — e.g. ``_workspaces`` contains
        ``.gitkeep`` markers and legitimate zero-byte placeholders.
        """
        exempt = {"__init__.py", ".gitkeep", "conftest.py"}
        ops: List[Dict[str, Any]] = []
        for f in ctx.all_files:
            if f.name in exempt:
                continue
            # Never delete inside protected directories
            try:
                rel = f.relative_to(self.workspace_root)
                if rel.parts and rel.parts[0] in PROTECTED_DIRS:
                    continue
            except ValueError:
                pass
            try:
                if f.stat().st_size == 0:
                    ops.append({"type": "delete", "source": f})
            except OSError:
                pass
        return ops

    def _plan_orphan_cleanup(
        self, ctx: FileContext
    ) -> List[Dict[str, Any]]:
        """Plan orphaned-directory removal.

        Skips directories inside PROTECTED_DIRS — ``_workspaces`` and
        ``cortex-sts`` intentionally contain subdirectory structures without
        Python files.
        """
        dirs_with_files = {f.parent for f in ctx.all_files}
        ops: List[Dict[str, Any]] = []
        for d in ctx.directories:
            if d in dirs_with_files or d == self.workspace_root:
                continue
            # Never rmdir inside protected directories
            try:
                rel = d.relative_to(self.workspace_root)
                if rel.parts and rel.parts[0] in PROTECTED_DIRS:
                    continue
            except ValueError:
                pass
            ops.append({"type": "rmdir", "source": d})
        return ops

    def _plan_markdown_archive(
        self, ctx: FileContext
    ) -> List[Dict[str, Any]]:
        """Plan stale-markdown archival.

        Skips files inside PROTECTED_DIRS (.github, cortex-docs, cortex-registry,
        etc.) to avoid archiving legitimate agent/prompt/spec markdown files.
        """
        doc_dirs = {"docs", "cortex-docs", "documentation"}
        ops: List[Dict[str, Any]] = []
        for f in ctx.all_files:
            if f.suffix != ".md":
                continue
            rel = f.relative_to(self.workspace_root)
            # Root-level protected names
            if len(rel.parts) == 1:
                stem = f.stem.upper()
                if any(stem.startswith(p) for p in ALLOWED_MARKDOWN_PREFIXES):
                    continue
            # Never touch files inside protected top-level dirs
            top_dir = rel.parts[0] if rel.parts else ""
            if top_dir in PROTECTED_DIRS or top_dir in doc_dirs:
                continue
            ops.append({
                "type": "relocate",
                "source": f,
                "dest_dir": self.workspace_root / ARCHIVE_DIR,
            })
        return ops

    def _execute_op(
        self, op: Dict[str, Any], *, dry_run: bool = False
    ) -> OperationResult:
        """Execute or preview a single planned operation."""
        op_type = op["type"]
        source: Path = op["source"]

        if dry_run:
            return OperationResult(
                op_type=op_type,
                source=source,
                destination=op.get("dest_dir"),
                success=True,
                dry_run=True,
            )

        if op_type == "rename":
            return self.rename_file(source, op["new_name"])
        elif op_type == "delete":
            return self.delete_file(source)
        elif op_type == "rmdir":
            return self.delete_directory(source)
        elif op_type == "relocate":
            return self.relocate_file(source, op["dest_dir"])
        else:
            return OperationResult(
                op_type=op_type, source=source, success=False,
                error=f"Unknown op type: {op_type}",
            )


    def _load_anti_patterns(self) -> Dict[str, Any]:
        """Load anti-pattern knowledge for structural detection.

        Phase 78 GAP-78-B-02: Wire engineering-anti-patterns knowledge so
        vacuum analysis detects structural anti-patterns (god classes, circular deps,
        feature envy) in addition to filesystem clutter.

        Returns:
            Dict with anti-pattern definitions and detection heuristics.
        """
        try:
            from cortex.intelligence.provider import get_intelligence_provider
            provider = get_intelligence_provider()
            return provider.get_best_practices("anti_patterns:engineering")
        except Exception:
            return {}

    def _get_anti_pattern_knowledge(self) -> Dict[str, Any]:
        """Return anti-pattern knowledge for current vacuum context.

        Phase 78 GAP-78-B-02: Convenience wrapper over _load_anti_patterns.

        Returns:
            Dict with structural anti-pattern detection heuristics.
        """
        return self._load_anti_patterns()

    def health_check(self) -> Dict[str, Any]:
        """Return health status of the VacuumOrchestrator.

        Returns:
            Mapping with ``status``, ``orchestrator``, and ``workspace_root`` keys.
        """
        return {
            "status": "healthy",
            "orchestrator": "VacuumOrchestrator",
            "workspace_root": str(self.workspace_root),
        }


__all__ = ["VacuumOrchestrator"]

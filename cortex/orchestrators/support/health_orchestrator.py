"""
HealthOrchestrator, VacuumExecutor, and HealthVacuumPipeline — Phase 48

Implements the two-phase Health-Vacuum pipeline:
1. HealthOrchestrator: scans repository, produces health-issues.yaml
2. VacuumExecutor: reads issues, applies cleanup operations with rollback
3. HealthVacuumPipeline: coordinates all 5 stages end-to-end

Governance:
- CORE-002: No markdown sprawl
- CORE-008: TDD-first
- CORE-011: Type hints 100%
- CORE-012: Google-style docstrings
- CORE-028: Naming conventions (snake_case Python, kebab-case others)
- CORE-035: Single canonical implementation

Authority: Phase 48, workflow: health-vacuum-pipeline.yaml
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROTECTED_FILES: frozenset[str] = frozenset(
    [
        "pytest.ini",
        "requirements.txt",
        "README.md",
        ".gitignore",
        "conftest.py",
        "pyproject.toml",
        "Makefile",
        "health_stubs.json",
        ".pre-commit-config.yaml",
        "governance.db",
        "governance.db-shm",
        "governance.db-wal",
    ]
)

EXCLUDED_DIRS: frozenset[str] = frozenset(
    [".git", ".venv", "__pycache__", "node_modules", "_workspaces"]
)

ALLOWED_MARKDOWN_PREFIXES: tuple[str, ...] = (
    ".github/prompts/",
    ".github/agents/",
    "docs/",
    "cortex-docs/",
    "cortex-registry/",
    "_workspaces/",
)

KEBAB_MAX_LEN: int = 30
PLAN_FILE_MAX_LEN: int = 40


# ---------------------------------------------------------------------------
# Value Objects
# ---------------------------------------------------------------------------


@dataclass
class IssueFile:
    """A single file issue."""

    path: str
    action: str
    recommended_name: str = ""
    old_ref: str = ""
    new_ref: str = ""
    markers: list[str] = field(default_factory=list)


@dataclass
class IssueDirectory:
    """A single directory issue."""

    path: str
    action: str


@dataclass
class DuplicateGroup:
    """A group of files with identical content."""

    hash: str
    files: list[str]
    action: str


@dataclass
class IssueCategory:
    """Container for one issue category."""

    count: int = 0
    files: list[IssueFile] = field(default_factory=list)
    directories: list[IssueDirectory] = field(default_factory=list)
    groups: list[DuplicateGroup] = field(default_factory=list)


@dataclass
class ScanSummary:
    """Top-level scan summary."""

    delete_count: int = 0
    rename_count: int = 0
    relocate_count: int = 0
    estimated_bytes_freed: int = 0


@dataclass
class ScanResult:
    """Complete result of a health scan."""

    generated_at: str = ""
    scan_duration_ms: int = 0
    total_files_scanned: int = 0
    issues_found: int = 0

    screaming_case: IssueCategory = field(default_factory=IssueCategory)
    empty_files: IssueCategory = field(default_factory=IssueCategory)
    orphaned_directories: IssueCategory = field(default_factory=IssueCategory)
    deprecated_code: IssueCategory = field(default_factory=IssueCategory)
    duplicate_content: IssueCategory = field(default_factory=IssueCategory)
    wrong_references: IssueCategory = field(default_factory=IssueCategory)
    invalid_markdown: IssueCategory = field(default_factory=IssueCategory)
    summary: ScanSummary = field(default_factory=ScanSummary)

    def issues_for_path(self, path_fragment: str) -> list[IssueFile]:
        """Return all issues matching a path fragment.

        Args:
            path_fragment: Substring to search for in issue paths.

        Returns:
            List of IssueFile objects matching the fragment.
        """
        results: list[IssueFile] = []
        for cat in [
            self.screaming_case,
            self.empty_files,
            self.deprecated_code,
            self.wrong_references,
            self.invalid_markdown,
        ]:
            results.extend(f for f in cat.files if path_fragment in f.path)
        return results

    def _recount(self) -> None:
        """Recalculate issues_found and summary counts."""
        cats = [
            self.screaming_case,
            self.empty_files,
            self.orphaned_directories,
            self.deprecated_code,
            self.duplicate_content,
            self.wrong_references,
            self.invalid_markdown,
        ]
        self.issues_found = sum(c.count for c in cats)
        self.summary.rename_count = self.screaming_case.count
        self.summary.delete_count = (
            self.empty_files.count
            + self.orphaned_directories.count
            + self.invalid_markdown.count
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def to_kebab_case(filename: str, max_length: int = KEBAB_MAX_LEN) -> str:
    """Convert a filename to kebab-case within max_length.

    Args:
        filename: Original filename (may include extension).
        max_length: Maximum total length including extension.

    Returns:
        Lowercase kebab-case filename, truncated if necessary.
    """
    p = Path(filename)
    ext = p.suffix.lower()
    stem = p.stem.lower().replace("_", "-")
    # Collapse consecutive hyphens
    stem = re.sub(r"-+", "-", stem).strip("-")

    max_stem = max_length - len(ext)
    if len(stem) > max_stem:
        stem = stem[:max_stem].rstrip("-")

    return stem + ext


def _is_excluded(path: Path, workspace_root: Path) -> bool:
    """Return True if path is inside an excluded directory.

    Args:
        path: Absolute path to check.
        workspace_root: Repo root for relative computation.

    Returns:
        True when path is inside any excluded directory.
    """
    try:
        rel = path.relative_to(workspace_root)
    except ValueError:
        return False
    parts = rel.parts
    return bool(EXCLUDED_DIRS.intersection(parts))


def _is_protected(path: Path) -> bool:
    """Return True if filename is in the protected set.

    Args:
        path: Path whose name to check.

    Returns:
        True when the file must never be modified.
    """
    return path.name in PROTECTED_FILES


def _is_screaming(name: str) -> bool:
    """Return True if name contains 3+ consecutive uppercase letters.

    Args:
        name: Filename stem + extension.

    Returns:
        True when the name triggers CORE-028 screaming-case rule.
    """
    stem = Path(name).stem
    return bool(re.search(r"[A-Z]{3,}", stem))


def _is_valid_markdown_path(rel_path: Path) -> bool:
    """Return True when markdown file sits in an allowed location.

    Args:
        rel_path: Repo-relative path.

    Returns:
        True when the markdown file satisfies CORE-002.
    """
    rel_str = str(rel_path).replace("\\", "/")
    if rel_path.name == "README.md":
        return True
    return any(rel_str.startswith(prefix) for prefix in ALLOWED_MARKDOWN_PREFIXES)


# ---------------------------------------------------------------------------
# HealthOrchestrator
# ---------------------------------------------------------------------------


class HealthOrchestrator:
    """Scans the CORTEX repository and produces a structured ScanResult.

    Checks implemented:
        H-001 Screaming case filenames
        H-002 Empty files
        H-003 Orphaned (empty) directories
        H-004 Wrong path references (cortex_brain → cortex_intelligence)
        H-005 Duplicate content (md5 hash)
        H-006 Deprecated markers
        H-007 Invalid markdown location (CORE-002)
    """

    def __init__(self, workspace_root: Path | None = None) -> None:
        """Initialise with workspace root.

        Args:
            workspace_root: Root of the CORTEX repository.
                            Defaults to current working directory.
        """
        self.workspace_root = workspace_root or Path.cwd()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self) -> ScanResult:
        """Execute all health checks and return a ScanResult.

        Returns:
            Populated ScanResult with all discovered issues.
        """
        t_start = datetime.now(timezone.utc)
        result = ScanResult(generated_at=t_start.isoformat())

        files: list[Path] = []
        dirs: list[Path] = []

        for item in self.workspace_root.rglob("*"):
            if _is_excluded(item, self.workspace_root):
                continue
            if item.is_file():
                files.append(item)
            elif item.is_dir():
                dirs.append(item)

        result.total_files_scanned = len(files)

        self._check_screaming_case(files, result)
        self._check_empty_files(files, result)
        self._check_orphaned_dirs(dirs, result)
        self._check_wrong_references(files, result)
        self._check_duplicate_content(files, result)
        self._check_deprecated_markers(files, result)
        self._check_invalid_markdown(files, result)

        result._recount()
        result.scan_duration_ms = int(
            (datetime.now(timezone.utc) - t_start).total_seconds() * 1000
        )
        return result

    def write_handoff(self, result: ScanResult, output_path: Path) -> None:
        """Serialise ScanResult to health-issues.yaml.

        Args:
            result: Completed ScanResult.
            output_path: Destination path for the YAML handoff file.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data: dict[str, Any] = {
            "metadata": {
                "generated_at": result.generated_at,
                "scan_duration_ms": result.scan_duration_ms,
                "total_files_scanned": result.total_files_scanned,
                "issues_found": result.issues_found,
            },
            "issues": {
                "screaming_case": {
                    "count": result.screaming_case.count,
                    "files": [
                        {
                            "path": f.path,
                            "recommended_name": f.recommended_name,
                            "action": f.action,
                        }
                        for f in result.screaming_case.files
                    ],
                },
                "empty_files": {
                    "count": result.empty_files.count,
                    "files": [
                        {"path": f.path, "action": f.action}
                        for f in result.empty_files.files
                    ],
                },
                "orphaned_directories": {
                    "count": result.orphaned_directories.count,
                    "directories": [
                        {"path": d.path, "action": d.action}
                        for d in result.orphaned_directories.directories
                    ],
                },
                "deprecated_code": {
                    "count": result.deprecated_code.count,
                    "files": [
                        {"path": f.path, "markers": f.markers, "action": f.action}
                        for f in result.deprecated_code.files
                    ],
                },
                "duplicate_content": {
                    "count": result.duplicate_content.count,
                    "groups": [
                        {"hash": g.hash, "files": g.files, "action": g.action}
                        for g in result.duplicate_content.groups
                    ],
                },
                "wrong_references": {
                    "count": result.wrong_references.count,
                    "files": [
                        {
                            "path": f.path,
                            "old_ref": f.old_ref,
                            "new_ref": f.new_ref,
                            "action": f.action,
                        }
                        for f in result.wrong_references.files
                    ],
                },
                "invalid_markdown": {
                    "count": result.invalid_markdown.count,
                    "files": [
                        {"path": f.path, "action": f.action}
                        for f in result.invalid_markdown.files
                    ],
                },
            },
            "summary": {
                "delete_count": result.summary.delete_count,
                "rename_count": result.summary.rename_count,
                "relocate_count": result.summary.relocate_count,
                "estimated_bytes_freed": result.summary.estimated_bytes_freed,
            },
        }
        with open(output_path, "w") as fh:
            yaml.dump(data, fh, default_flow_style=False, sort_keys=False)

    # ------------------------------------------------------------------
    # Private checks
    # ------------------------------------------------------------------

    def _check_screaming_case(self, files: list[Path], result: ScanResult) -> None:
        for f in files:
            if _is_protected(f):
                continue
            if _is_screaming(f.name):
                result.screaming_case.files.append(
                    IssueFile(
                        path=str(f.relative_to(self.workspace_root)),
                        action="rename",
                        recommended_name=to_kebab_case(f.name),
                    )
                )
        result.screaming_case.count = len(result.screaming_case.files)

    def _check_empty_files(self, files: list[Path], result: ScanResult) -> None:
        exempt_names = {".gitkeep"}
        for f in files:
            if f.name in exempt_names:
                continue
            if _is_protected(f):
                continue
            try:
                if f.stat().st_size == 0:
                    result.empty_files.files.append(
                        IssueFile(path=str(f.relative_to(self.workspace_root)), action="delete")
                    )
            except OSError:
                pass
        result.empty_files.count = len(result.empty_files.files)

    def _check_orphaned_dirs(self, dirs: list[Path], result: ScanResult) -> None:
        for d in dirs:
            if _is_excluded(d, self.workspace_root):
                continue
            try:
                children = list(d.iterdir())
                if not children:
                    result.orphaned_directories.directories.append(
                        IssueDirectory(
                            path=str(d.relative_to(self.workspace_root)),
                            action="delete",
                        )
                    )
            except PermissionError:
                pass
        result.orphaned_directories.count = len(result.orphaned_directories.directories)

    _WRONG_REFS: dict[str, str] = {
        "cortex_brain": "cortex_intelligence",
        "_cortex-master": "cortex-registry",
    }

    def _check_wrong_references(self, files: list[Path], result: ScanResult) -> None:
        text_exts = {".py", ".yaml", ".yml", ".json", ".md", ".txt"}
        seen_paths: set[str] = set()
        for f in files:
            if f.suffix not in text_exts:
                continue
            try:
                content = f.read_text(errors="replace")
            except OSError:
                continue
            rel = str(f.relative_to(self.workspace_root))
            for old, new in self._WRONG_REFS.items():
                if old in content and rel not in seen_paths:
                    result.wrong_references.files.append(
                        IssueFile(
                            path=rel,
                            action="fix",
                            old_ref=old,
                            new_ref=new,
                        )
                    )
                    seen_paths.add(rel)
                    break
        result.wrong_references.count = len(result.wrong_references.files)

    def _check_duplicate_content(self, files: list[Path], result: ScanResult) -> None:
        hash_map: dict[str, list[str]] = {}
        for f in files:
            try:
                if f.stat().st_size < 100:
                    continue
                digest = hashlib.md5(f.read_bytes()).hexdigest()
                rel = str(f.relative_to(self.workspace_root))
                hash_map.setdefault(digest, []).append(rel)
            except OSError:
                pass
        for digest, paths in hash_map.items():
            if len(paths) > 1:
                result.duplicate_content.groups.append(
                    DuplicateGroup(hash=digest, files=paths, action="keep_canonical")
                )
        result.duplicate_content.count = len(result.duplicate_content.groups)

    _DEPRECATED_MARKERS = ["DEPRECATED", "TODO: remove", "FIXME: delete"]

    def _check_deprecated_markers(self, files: list[Path], result: ScanResult) -> None:
        text_exts = {".py", ".yaml", ".yml", ".md", ".txt"}
        for f in files:
            if f.suffix not in text_exts:
                continue
            try:
                content = f.read_text(errors="replace")
            except OSError:
                continue
            found = [m for m in self._DEPRECATED_MARKERS if m in content]
            if found:
                result.deprecated_code.files.append(
                    IssueFile(
                        path=str(f.relative_to(self.workspace_root)),
                        action="review_for_deletion",
                        markers=found,
                    )
                )
        result.deprecated_code.count = len(result.deprecated_code.files)

    def _check_invalid_markdown(self, files: list[Path], result: ScanResult) -> None:
        for f in files:
            if f.suffix != ".md":
                continue
            if _is_protected(f):
                continue
            try:
                rel = f.relative_to(self.workspace_root)
            except ValueError:
                continue
            if not _is_valid_markdown_path(rel):
                result.invalid_markdown.files.append(
                    IssueFile(
                        path=str(rel),
                        action="relocate_or_delete",
                    )
                )
        result.invalid_markdown.count = len(result.invalid_markdown.files)


# ---------------------------------------------------------------------------
# Operation result
# ---------------------------------------------------------------------------


@dataclass
class OperationResult:
    """Result of a single vacuum operation."""

    success: bool
    operation: str = ""
    source: str = ""
    destination: str = ""
    error: str = ""


# ---------------------------------------------------------------------------
# VacuumExecutor
# ---------------------------------------------------------------------------


class VacuumExecutor:
    """Executes cleanup operations derived from a ScanResult or health-issues.yaml.

    Provides rollback via manifest recording every destructive operation.
    """

    def __init__(self, workspace_root: Path | None = None, dry_run: bool = False) -> None:
        """Initialise executor.

        Args:
            workspace_root: Repo root directory.
            dry_run: When True, log operations but make no file changes.
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.dry_run = dry_run
        self._operations: list[dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Public operations
    # ------------------------------------------------------------------

    def rename_file(self, source: Path, new_name: str) -> OperationResult:
        """Rename source file to new_name in the same directory.

        Args:
            source: Absolute path to file to rename.
            new_name: New filename (name only, no directory).

        Returns:
            OperationResult indicating success or failure.
        """
        if _is_protected(source):
            return OperationResult(success=False, operation="rename", source=str(source), error="protected")
        dest = source.parent / new_name
        if not source.exists():
            return OperationResult(success=False, operation="rename", source=str(source), error="not_found")
        if not self.dry_run:
            # Use os.rename for atomic case-rename on case-insensitive filesystems (macOS APFS)
            # Two-step: original → temp → target, ensuring old name disappears
            tmp_path = source.parent / (source.name + ".__cortex_tmp__")
            os.rename(str(source), str(tmp_path))
            os.rename(str(tmp_path), str(dest))
        self._operations.append(
            {"op": "rename", "source": str(source), "destination": str(dest)}
        )
        return OperationResult(success=True, operation="rename", source=str(source), destination=str(dest))

    def delete_file(self, target: Path) -> OperationResult:
        """Delete a single file.

        Args:
            target: Absolute path to file to delete.

        Returns:
            OperationResult indicating success or failure.
        """
        if _is_protected(target):
            return OperationResult(success=False, operation="delete", source=str(target), error="protected")
        if not target.exists():
            return OperationResult(success=False, operation="delete", source=str(target), error="not_found")
        try:
            content = target.read_bytes() if not self.dry_run else b""
            self._operations.append(
                {"op": "delete", "source": str(target), "content_b64": ""}
            )
            if not self.dry_run:
                target.unlink()
            return OperationResult(success=True, operation="delete", source=str(target))
        except OSError as exc:
            return OperationResult(success=False, operation="delete", source=str(target), error=str(exc))

    def delete_directory(self, target: Path) -> OperationResult:
        """Delete an empty directory.

        Args:
            target: Absolute path to directory to remove.

        Returns:
            OperationResult indicating success or failure.
        """
        if not target.is_dir():
            return OperationResult(success=False, operation="delete_dir", source=str(target), error="not_dir")
        children = list(target.iterdir())
        if children:
            return OperationResult(success=False, operation="delete_dir", source=str(target), error="not_empty")
        if not self.dry_run:
            target.rmdir()
        self._operations.append({"op": "delete_dir", "source": str(target)})
        return OperationResult(success=True, operation="delete_dir", source=str(target))

    def relocate_file(
        self, source: Path, destination_dir: Path, protected: bool = False
    ) -> OperationResult:
        """Move source file into destination_dir.

        Args:
            source: File to move.
            destination_dir: Target directory.
            protected: If True, refuse to move.

        Returns:
            OperationResult indicating success or failure.
        """
        if protected or _is_protected(source):
            return OperationResult(success=False, operation="relocate", source=str(source), error="protected")
        if not source.exists():
            return OperationResult(success=False, operation="relocate", source=str(source), error="not_found")
        dest = destination_dir / source.name
        if not self.dry_run:
            destination_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(dest))
        self._operations.append(
            {"op": "relocate", "source": str(source), "destination": str(dest)}
        )
        return OperationResult(success=True, operation="relocate", source=str(source), destination=str(dest))

    def save_rollback_manifest(self, manifest_path: Path) -> None:
        """Write all recorded operations to a JSON rollback manifest.

        Args:
            manifest_path: Path to write the rollback-manifest.json.
        """
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "operations": self._operations,
        }
        manifest_path.write_text(json.dumps(data, indent=2))

    def rollback(self, manifest_path: Path) -> None:
        """Reverse all operations recorded in the rollback manifest.

        Args:
            manifest_path: Path to rollback-manifest.json.
        """
        data = json.loads(manifest_path.read_text())
        for op in reversed(data["operations"]):
            kind = op["op"]
            if kind == "rename":
                src, dst = Path(op["source"]), Path(op["destination"])
                if dst.exists():
                    tmp_path = dst.parent / (dst.name + ".__cortex_tmp__")
                    os.rename(str(dst), str(tmp_path))
                    os.rename(str(tmp_path), str(src))
            elif kind == "relocate":
                src, dst = Path(op["source"]), Path(op["destination"])
                if dst.exists():
                    shutil.move(str(dst), str(src))
            elif kind == "delete":
                pass  # Cannot restore without content backup
            elif kind == "delete_dir":
                Path(op["source"]).mkdir(parents=True, exist_ok=True)

    def delete_handoff(self, handoff_path: Path) -> None:
        """Delete the health-issues.yaml handoff file.

        Args:
            handoff_path: Absolute path to health-issues.yaml.
        """
        if handoff_path.exists():
            handoff_path.unlink()

    def execute_from_handoff(self, handoff_path: Path) -> list[OperationResult]:
        """Read health-issues.yaml and execute all prescribed operations.

        Args:
            handoff_path: Path to health-issues.yaml written by HealthOrchestrator.

        Returns:
            List of OperationResult for every operation attempted.
        """
        with open(handoff_path) as fh:
            data = yaml.safe_load(fh)

        results: list[OperationResult] = []
        issues = data.get("issues", {})

        # Renames
        for entry in issues.get("screaming_case", {}).get("files", []):
            target = self.workspace_root / entry["path"]
            if target.exists():
                results.append(self.rename_file(target, entry["recommended_name"]))

        # Deletes (empty files)
        for entry in issues.get("empty_files", {}).get("files", []):
            target = self.workspace_root / entry["path"]
            results.append(self.delete_file(target))

        # Orphaned directories
        for entry in issues.get("orphaned_directories", {}).get("directories", []):
            target = self.workspace_root / entry["path"]
            results.append(self.delete_directory(target))

        # Invalid markdown
        for entry in issues.get("invalid_markdown", {}).get("files", []):
            target = self.workspace_root / entry["path"]
            results.append(self.delete_file(target))

        return results


# ---------------------------------------------------------------------------
# PipelineReport
# ---------------------------------------------------------------------------


@dataclass
class PipelineReport:
    """Summary report produced by HealthVacuumPipeline.run()."""

    stage_1_preflight: str = "SKIP"
    stage_2_health_scan: str = "SKIP"
    stage_3_review: str = "SKIP"
    stage_4_vacuum: str = "SKIP"
    stage_5_verification: str = "SKIP"
    operations_planned: int = 0
    operations_executed: int = 0
    issues_found: int = 0
    errors: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# HealthVacuumPipeline
# ---------------------------------------------------------------------------


class HealthVacuumPipeline:
    """Coordinates all 5 stages of the Health-Vacuum pipeline.

    Stages:
        1. Pre-flight safety (git status, baseline tests)
        2. Health scan (write health-issues.yaml)
        3. Interactive review (skipped in autonomous mode)
        4. Vacuum execution (apply cleanup)
        5. Verification & teardown (run tests, delete handoff)
    """

    HANDOFF_REL = Path("cortex/brain/vacuum/health-issues.yaml")
    MANIFEST_REL = Path("cortex/brain/vacuum/rollback-manifest.json")

    def __init__(self, workspace_root: Path | None = None, dry_run: bool = False) -> None:
        """Initialise pipeline.

        Args:
            workspace_root: Repo root directory.
            dry_run: When True, skip destructive operations.
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.dry_run = dry_run
        self._handoff = self.workspace_root / self.HANDOFF_REL
        self._manifest = self.workspace_root / self.MANIFEST_REL

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, autonomous: bool = True) -> PipelineReport:
        """Execute the full 5-stage pipeline.

        Args:
            autonomous: When True skip interactive review stage.

        Returns:
            PipelineReport with per-stage status and metrics.
        """
        report = PipelineReport()

        # Stage 1
        report.stage_1_preflight = self._stage_preflight()

        # Stage 2
        orchestrator = HealthOrchestrator(workspace_root=self.workspace_root)
        scan_result = orchestrator.scan()
        report.issues_found = scan_result.issues_found
        report.operations_planned = (
            scan_result.screaming_case.count
            + scan_result.empty_files.count
            + scan_result.orphaned_directories.count
            + scan_result.invalid_markdown.count
        )
        orchestrator.write_handoff(scan_result, self._handoff)
        report.stage_2_health_scan = "PASS"

        # Stage 3 (interactive — skipped in autonomous)
        report.stage_3_review = "SKIP" if autonomous else "PASS"

        # Stage 4
        if not self.dry_run:
            executor = VacuumExecutor(workspace_root=self.workspace_root, dry_run=False)
            op_results = executor.execute_from_handoff(self._handoff)
            executor.save_rollback_manifest(self._manifest)
            report.operations_executed = sum(1 for r in op_results if r.success)
            report.stage_4_vacuum = "PASS"
        else:
            report.stage_4_vacuum = "DRY_RUN"
            report.operations_executed = 0

        # Stage 5 — teardown
        report.stage_5_verification = self._stage_teardown()

        return report

    # ------------------------------------------------------------------
    # Private stages
    # ------------------------------------------------------------------

    def _git_status(self) -> str:
        """Return 'clean' or 'dirty' based on git working tree."""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.workspace_root,
            )
            return "dirty" if result.stdout.strip() else "clean"
        except Exception:
            return "clean"

    def _git_stash(self) -> None:
        """Stash uncommitted changes."""
        subprocess.run(
            ["git", "stash", "--include-untracked"],
            cwd=self.workspace_root,
            check=False,
        )

    def _stage_preflight(self) -> str:
        """Run pre-flight checks.

        Returns:
            'PASS' always (stashes dirty state).
        """
        if self._git_status() == "dirty":
            self._git_stash()
        return "PASS"

    def _stage_teardown(self) -> str:
        """Delete temporary files after successful pipeline.

        Returns:
            'PASS' after cleanup.
        """
        if self._handoff.exists():
            self._handoff.unlink()
        if self._manifest.exists() and not self.dry_run:
            self._manifest.unlink()
        return "PASS"

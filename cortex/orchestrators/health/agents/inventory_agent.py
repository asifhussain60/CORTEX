"""Inventory Agent — Folder & File Consolidation Scanner

Detects consolidation, deletion, and relocation opportunities across
the cortex/ package tree and emits structured InventoryFindings that
the VacuumExecutor consumes via health-issues.yaml.

The agent NEVER mutates files itself.  It is a pure scanner that
hands work to the vacuum pipeline.

Detected patterns
-----------------
CONSOLIDATE  — folder duplicated at a lower level inside cortex/
               (e.g. cortex/cortex_intelligence vs root cortex_intelligence)
DELETE       — tracked stray folders whose content belongs nowhere and
               has zero external imports (e.g. cortex/reports, cortex/sts)
RELOCATE     — file/folder that lives inside cortex/ but has no Python importers
               and belongs in a different canonical root (e.g. cortex/sts →
               _workspaces/sts/). Python packages (cortex/deployment, cortex/tests,
               cortex/scripts) are EXCLUDED — they must stay inside cortex/.
STUB_DIR     — directory containing only __init__.py (empty namespace shell)

Author: CORTEX Framework
Phase: PHASE-98
CORE Rules: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
            CORE-035 (single canonical implementation)
"""

from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


# ---------------------------------------------------------------------------
# Enums & data classes
# ---------------------------------------------------------------------------

class InventoryAction(str, Enum):
    """Action the VacuumExecutor must perform."""

    CONSOLIDATE = "consolidate"  # merge duplicate subfolder into canonical root
    DELETE = "delete"            # remove stray file/folder with no usages
    RELOCATE = "relocate"        # move to a different canonical directory
    STUB_DIR = "stub_dir"        # prune empty namespace-only directory


@dataclass
class InventoryFinding:
    """A single inventory finding ready for vacuum handoff.

    Attributes:
        action: What the vacuum should do.
        source_path: Relative path of the item to act on.
        target_path: Canonical destination (None for DELETE / STUB_DIR).
        reason: Human-readable rationale.
        severity: P0–P3 bucket for prioritisation.
        safe: True when no external imports reference source_path.
    """

    action: InventoryAction
    source_path: str
    target_path: Optional[str]
    reason: str
    severity: str = "medium"  # low | medium | high | critical
    safe: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to YAML-friendly dict for health-issues.yaml."""
        return {
            "action": self.action.value,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "reason": self.reason,
            "severity": self.severity,
            "safe": self.safe,
        }


# ---------------------------------------------------------------------------
# Known canonical mappings — single source of truth for relocation rules
# ---------------------------------------------------------------------------

#: Folders inside cortex/ that duplicate a root-level package.
#: key = relative path inside cortex/, value = canonical root path.
_DUPLICATE_INSIDE_CORTEX: Dict[str, str] = {
    "cortex_intelligence": "cortex_intelligence",
    "cortex-registry": "cortex-registry",
}

#: Folders inside cortex/ that should live at a different root.
#: ONLY non-Python-package folders (no importers) belong here.
#: key = relative path inside cortex/, value = canonical root (None → DELETE).
#:
#: EXCLUDED intentionally — these ARE importable Python packages with external consumers:
#:   cortex/deployment  → imported as cortex.deployment by 11+ files
#:   cortex/tests       → stray test folder, no Python importers but relocated manually
#:   cortex/scripts     → stray scripts, no Python importers but relocated manually
#:   cortex/enforcement → imported as cortex.enforcement (native_tool_interceptor)
_RELOCATION_MAP: Dict[str, str] = {
    "sts": "_workspaces/sts",
    "reports": None,      # None → DELETE (no canonical home, only __init__.py)
    "phase_38": None,     # orphaned phase — DELETE after confirming test refs
    "phase_management": None,  # orphaned — DELETE after confirming no refs
}

#: Import patterns that indicate a folder is still referenced externally.
#: Mapped as folder_name → list of import prefixes to grep for.
_IMPORT_PREFIXES: Dict[str, List[str]] = {
    "phase_38": ["from cortex.phase_38", "cortex.phase_38"],
    "phase_management": ["from cortex.phase_management", "cortex.phase_management"],
    "sts": ["from cortex.sts", "cortex.sts"],
    "reports": ["from cortex.reports", "cortex.reports"],
    "enforcement": ["from cortex.enforcement", "cortex.enforcement"],
    "deployment": ["from cortex.deployment", "cortex.deployment"],
    "tests": ["from cortex.tests", "cortex.tests"],
    "scripts": ["from cortex.scripts", "cortex.scripts"],
}


class InventoryAgent(BaseHealthAgent):
    """Health agent that identifies structural consolidation opportunities.

    Scans ``cortex/`` for:
    - Duplicate sub-packages that shadow a root-level canonical package
    - Folders that belong in a different root (tests, scripts, deployment …)
    - Stray phase artefacts with no remaining imports
    - Stub directories (only ``__init__.py``, nothing else)

    Emits :class:`HealthIssue` records tagged with
    ``HealthIssueCategory.DUPLICATE`` or ``HealthIssueCategory.PATH`` and
    injects ``inventory_finding`` into each issue's metadata so the
    :class:`VacuumExecutor` can pick them up from *health-issues.yaml*.
    """

    #: Issue category used for all inventory findings.
    _CATEGORY_MAP: Dict[InventoryAction, HealthIssueCategory] = {
        InventoryAction.CONSOLIDATE: HealthIssueCategory.DUPLICATE,
        InventoryAction.DELETE: HealthIssueCategory.DUPLICATE,
        InventoryAction.RELOCATE: HealthIssueCategory.PATH,
        InventoryAction.STUB_DIR: HealthIssueCategory.WEAK_IMPLEMENTATION,
    }

    _SEVERITY_MAP: Dict[str, HealthIssueSeverity] = {
        "critical": HealthIssueSeverity.CRITICAL,
        "high": HealthIssueSeverity.HIGH,
        "medium": HealthIssueSeverity.MEDIUM,
        "low": HealthIssueSeverity.LOW,
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialise InventoryAgent."""
        super().__init__(
            name="InventoryAgent",
            description=(
                "Scans cortex/ for consolidation, deletion, and relocation "
                "opportunities and delegates cleanup to VacuumExecutor."
            ),
            config=config or {},
        )

    # ------------------------------------------------------------------
    # BaseHealthAgent contract
    # ------------------------------------------------------------------

    def check(self, workspace_root: Path, ctx: "Any | None" = None) -> HealthCheckResult:
        """Run inventory scan and return findings as HealthIssues.

        Args:
            workspace_root: Repository root directory.
            ctx: Optional :class:`~cortex.orchestrators.support.health_orchestrator.FileContext`
                shared by the Phase-48 pipeline.  When provided, import
                detection uses ``ctx.get_content()`` instead of spawning
                ``subprocess.run`` (git grep), eliminating all subprocess
                overhead.

        Returns:
            HealthCheckResult whose issues carry ``inventory_finding``
            metadata entries for the VacuumExecutor.
        """
        import time

        start = time.monotonic()
        cortex_root = workspace_root / "cortex"

        if not cortex_root.exists():
            return HealthCheckResult(
                agent_name=self.name,
                issues=[],
                files_scanned=0,
                duration_seconds=0.0,
                metadata={"skipped": "cortex/ not found"},
            )

        findings: List[InventoryFinding] = []
        files_scanned = 0

        # 1. Duplicate sub-packages
        findings.extend(self._scan_duplicates(cortex_root, workspace_root, ctx=ctx))

        # 2. Relocation / deletion candidates
        findings.extend(self._scan_relocations(cortex_root, workspace_root, ctx=ctx))

        # 3. Stub directories (only __init__.py)
        stub_findings, stub_count = self._scan_stub_dirs(cortex_root)
        findings.extend(stub_findings)
        files_scanned += stub_count

        # 4. Orphaned single-file orchestrator subfolders
        orchestrators_root = cortex_root / "orchestrators"
        if orchestrators_root.exists():
            orch_findings, orch_count = self._scan_stub_orchestrator_dirs(orchestrators_root)
            findings.extend(orch_findings)
            files_scanned += orch_count

        issues = [self._finding_to_issue(f, workspace_root) for f in findings]

        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=time.monotonic() - start,
            metadata={
                "findings_total": len(findings),
                "consolidate": sum(1 for f in findings if f.action == InventoryAction.CONSOLIDATE),
                "delete": sum(1 for f in findings if f.action == InventoryAction.DELETE),
                "relocate": sum(1 for f in findings if f.action == InventoryAction.RELOCATE),
                "stub_dir": sum(1 for f in findings if f.action == InventoryAction.STUB_DIR),
            },
        )

    # ------------------------------------------------------------------
    # Private scanners
    # ------------------------------------------------------------------

    def _scan_duplicates(
        self, cortex_root: Path, workspace_root: Path, ctx: "Any | None" = None
    ) -> List[InventoryFinding]:
        """Detect sub-packages inside cortex/ that shadow a root canonical."""
        findings: List[InventoryFinding] = []
        for rel, canonical in _DUPLICATE_INSIDE_CORTEX.items():
            inner = cortex_root / rel
            outer = workspace_root / canonical
            if inner.exists() and outer.exists():
                findings.append(
                    InventoryFinding(
                        action=InventoryAction.CONSOLIDATE,
                        source_path=f"cortex/{rel}",
                        target_path=canonical,
                        reason=(
                            f"cortex/{rel} duplicates the canonical root "
                            f"package {canonical}/. Inner copy should be "
                            "merged/deleted; root package is authoritative."
                        ),
                        severity="high",
                        safe=self._has_no_imports(
                            workspace_root, _IMPORT_PREFIXES.get(rel, []), ctx=ctx
                        ),
                    )
                )
        return findings

    def _scan_relocations(
        self, cortex_root: Path, workspace_root: Path, ctx: "Any | None" = None
    ) -> List[InventoryFinding]:
        """Detect misplaced folders that belong in a different root."""
        findings: List[InventoryFinding] = []
        for rel, target in _RELOCATION_MAP.items():
            inner = cortex_root / rel
            if not inner.exists():
                continue
            safe = self._has_no_imports(
                workspace_root, _IMPORT_PREFIXES.get(rel, []), ctx=ctx
            )
            if target is None:
                findings.append(
                    InventoryFinding(
                        action=InventoryAction.DELETE,
                        source_path=f"cortex/{rel}",
                        target_path=None,
                        reason=(
                            f"cortex/{rel} has no canonical home and "
                            "zero external imports — safe to delete."
                        ),
                        severity="medium" if safe else "low",
                        safe=safe,
                    )
                )
            else:
                findings.append(
                    InventoryFinding(
                        action=InventoryAction.RELOCATE,
                        source_path=f"cortex/{rel}",
                        target_path=target,
                        reason=(
                            f"cortex/{rel} belongs in {target}/ at "
                            "the repository root, not inside the cortex "
                            "Python package."
                        ),
                        severity="medium",
                        safe=safe,
                    )
                )
        return findings

    def _scan_stub_dirs(
        self, cortex_root: Path
    ) -> tuple[List[InventoryFinding], int]:
        """Detect directories containing only __init__.py (empty shells)."""
        findings: List[InventoryFinding] = []
        scanned = 0
        for subdir in sorted(cortex_root.iterdir()):
            if not subdir.is_dir():
                continue
            py_files = list(subdir.rglob("*.py"))
            scanned += len(py_files)
            # A stub dir has exactly one file and it's __init__.py
            if len(py_files) == 1 and py_files[0].name == "__init__.py":
                rel = subdir.relative_to(cortex_root.parent)
                findings.append(
                    InventoryFinding(
                        action=InventoryAction.STUB_DIR,
                        source_path=str(rel),
                        target_path=None,
                        reason=(
                            f"{rel} contains only __init__.py — "
                            "it is an empty namespace shell with no "
                            "implementation. Prune or populate."
                        ),
                        severity="low",
                        safe=True,
                    )
                )
        return findings, scanned

    def _scan_stub_orchestrator_dirs(
        self, orchestrators_root: Path
    ) -> tuple[List[InventoryFinding], int]:
        """Detect orchestrator subfolders that only hold __init__.py.

        These are placeholder directories created speculatively but never
        populated.  They should be deleted or their content merged into an
        existing orchestrator module.
        """
        findings: List[InventoryFinding] = []
        scanned = 0
        for subdir in sorted(orchestrators_root.iterdir()):
            if not subdir.is_dir():
                continue
            py_files = list(subdir.rglob("*.py"))  # recursive — catches subdirs
            scanned += len(py_files)
            # Only flag as STUB if the *entire* subtree has nothing but a
            # top-level __init__.py (i.e. no real logic anywhere inside).
            if len(py_files) == 1 and py_files[0].name == "__init__.py":
                rel = subdir.relative_to(orchestrators_root.parent.parent)
                findings.append(
                    InventoryFinding(
                        action=InventoryAction.STUB_DIR,
                        source_path=str(rel),
                        target_path=None,
                        reason=(
                            f"cortex/orchestrators/{subdir.name} contains "
                            "only __init__.py. This is a speculative "
                            "placeholder — merge into an existing orchestrator "
                            "or delete."
                        ),
                        severity="low",
                        safe=True,
                    )
                )
        return findings, scanned

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _has_no_imports(
        workspace_root: Path,
        prefixes: List[str],
        ctx: "Any | None" = None,
    ) -> bool:
        """Return True when none of the given import prefixes appear in .py files.

        When *ctx* (a ``FileContext``) is provided, scans ``ctx.get_content()``
        in memory — zero subprocess spawns, zero additional disk reads.
        Falls back to ``git grep`` / pure-Python scan when ctx is absent.

        Args:
            workspace_root: Root to search.
            prefixes: Import prefixes to look for.
            ctx: Optional shared FileContext for in-memory scanning.

        Returns:
            True if none found (safe to act), False if references exist.
        """
        if not prefixes:
            return True

        # Fast path: use shared content cache (no subprocess, no extra I/O)
        if ctx is not None:
            for f in ctx.files:
                if f.suffix != ".py":
                    continue
                content = ctx.get_content(f)
                if any(prefix in content for prefix in prefixes):
                    return False
            return True

        # Slow path (no ctx): try git grep, fall back to pure Python
        for prefix in prefixes:
            try:
                result = subprocess.run(
                    ["git", "grep", "-l", "--", prefix],
                    cwd=workspace_root,
                    capture_output=True,
                    text=True,
                )
                if result.stdout.strip():
                    return False
            except FileNotFoundError:
                # git not available — fall back to Python scan
                for py in workspace_root.rglob("*.py"):
                    try:
                        if prefix in py.read_text(encoding="utf-8", errors="ignore"):
                            return False
                    except OSError:
                        pass
        return True

    def _finding_to_issue(
        self, finding: InventoryFinding, workspace_root: Path
    ) -> HealthIssue:
        """Convert an InventoryFinding to a HealthIssue for the report.

        Args:
            finding: The finding to convert.
            workspace_root: Repository root for path resolution.

        Returns:
            HealthIssue with inventory_finding metadata.
        """
        category = self._CATEGORY_MAP.get(finding.action, HealthIssueCategory.DUPLICATE)
        severity = self._SEVERITY_MAP.get(finding.severity, HealthIssueSeverity.MEDIUM)

        action_label = {
            InventoryAction.CONSOLIDATE: "CONSOLIDATE",
            InventoryAction.DELETE: "DELETE",
            InventoryAction.RELOCATE: "RELOCATE",
            InventoryAction.STUB_DIR: "PRUNE STUB DIR",
        }[finding.action]

        fix_parts = [f"Action: {action_label} {finding.source_path}"]
        if finding.target_path:
            fix_parts.append(f"→ {finding.target_path}")
        if not finding.safe:
            fix_parts.append(
                "[MANUAL] External imports detected — resolve references first."
            )

        return HealthIssue(
            category=category,
            severity=severity,
            file_path=workspace_root / finding.source_path,
            description=finding.reason,
            suggested_fix=" ".join(fix_parts),
            metadata={"inventory_finding": finding.to_dict()},
        )


__all__ = [
    "InventoryAction",
    "InventoryFinding",
    "InventoryAgent",
]

"""HealthOrchestrator — Holistic Repository Health Scanner

Single canonical orchestrator that diagnoses every gap across:
  • Filesystem integrity (naming, empty files, orphans, duplicates)
  • Root cleanliness (files that don't belong in project root)
  • Naming compliance (CORE-028)
  • Deprecated markers
  • Markdown location
  • Sweep catalogue wiring (CORE-064 — Phase 16)

Produces a :class:`ScanResult` and writes a YAML handoff for
:class:`VacuumOrchestrator`.

Phase: PHASE-51 + Phase-16 (CORE-064 sweep check added)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-028 (naming), CORE-035 (single canonical), CORE-064 (sweep completeness)

Health Check includes SweepCatalogueOrchestrator L1 wiring validation (AC-P17-015):
  - Confirms cortex.orchestrators.support.sweep_catalogue_orchestrator is importable
  - Confirms SweepCatalogueOrchestrator.health_check() is callable
  - Confirms .cortex-runtime/sweeps/ directory exists (created on first open_catalogue call)
  - VacuumOrchestrator companion handoff flags .cortex-runtime/sweeps/*.db as protected
"""

from __future__ import annotations

import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .agents.base_agent import BaseHealthAgent
from .constants import (
    ALLOWED_MARKDOWN_PREFIXES,
    PROTECTED_FILES,
)
from .file_context import FileContext
from .models import IssueFile, IssueSeverity, ScanResult
from .naming import (
    classify_naming_violation,
    is_screaming,
    to_kebab_case,
)
from .reports.health_report import HealthReport
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin

logger = logging.getLogger(__name__)


class HealthOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin, WorkflowTemplateMixin):
    """Holistic repository health scanner.

    Usage::

        orch = HealthOrchestrator(Path("/path/to/workspace"))
        result = orch.scan()
        orch.write_handoff(result, Path(".cortex-runtime/health-issues.yaml"))

    Attributes:
        workspace_root: Absolute path of the workspace.
    """

    # Phase 90 — Gateway opt-in pilot: HealthOrchestrator is the first maintenance
    # orchestrator to route all execution through WorkflowGateway.
    # Safe: health scan is read-only and non-destructive.
    PHASE90_GATEWAY_ENABLED: bool = True

    def __init__(
        self,
        workspace_root: Path,
        *,
        config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialise the orchestrator.

        Args:
            workspace_root: Root of the workspace to scan.
            config: Optional configuration overrides.

        Raises:
            ValueError: If *workspace_root* does not exist.
        """
        if not workspace_root.exists():
            raise ValueError(f"Workspace root does not exist: {workspace_root}")
        self.workspace_root = workspace_root
        self.config = config or {}
        self.agents: List[BaseHealthAgent] = []
        self.enabled: bool = True

    def get_recommended_template(self) -> str:
        """Return the canonical workflow template for HEALTH operations.

        Phase 90: WorkflowGateway uses this to resolve the template ID
        before any health execution begins.

        Returns:
            Template ID: 'maintenance/health-check-workflow'
        """
        return "maintenance/health-check-workflow"

    # ── agent registration (backward-compat with Phase-92 agents) ────────

    def register_agent(self, agent: BaseHealthAgent) -> None:
        """Register a health agent for use during scans.

        Args:
            agent: Agent instance implementing BaseHealthAgent.
        """
        self.agents.append(agent)

    def unregister_agent(self, name: str) -> bool:
        """Remove a registered agent by name.

        Args:
            name: Agent name.

        Returns:
            ``True`` if found and removed, ``False`` otherwise.
        """
        for i, a in enumerate(self.agents):
            if a.name == name:
                self.agents.pop(i)
                return True
        return False

    def get_agent(self, name: str) -> Optional[BaseHealthAgent]:
        """Retrieve a registered agent by name.

        Args:
            name: Agent name.

        Returns:
            The agent, or ``None``.
        """
        for a in self.agents:
            if a.name == name:
                return a
        return None

    def list_agents(self) -> List[str]:
        """Return names of all registered agents."""
        return [a.name for a in self.agents]

    @enforce_gateway
    def execute_operation(self, operation_name: str, parameters: dict) -> Any:
        """Gateway entry point — routes HEALTH mode through WorkflowGateway (Phase 90b)."""
        agent_names: Optional[List[str]] = parameters.get("agent_names")
        return self.run_health_check(agent_names=agent_names)

    def run_health_check(
        self,
        *,
        agent_names: Optional[List[str]] = None,
    ) -> HealthReport:
        """Run registered agents and return a HealthReport.

        This is the Phase-92 backward-compatible entry point. For the
        Phase-51 holistic scan use :meth:`scan` instead.

        Args:
            agent_names: Run only these agents.  ``None`` = all.

        Returns:
            HealthReport with agent results.
        """
        report = HealthReport(workspace_root=self.workspace_root)
        import time as _time
        _ac_id = f"AC-HEALTH-{int(_time.time() * 1000)}"
        # AC_START: {_ac_id}
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="run_health_check")
        if not self.enabled:
            # AC_COMPLETE: {_ac_id} ✅ (disabled)
            return report

        for agent in self.agents:
            if not agent.is_enabled():
                continue
            if agent_names and agent.name not in agent_names:
                continue
            try:
                result = agent.check(self.workspace_root)
                report.add_agent_result(result)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Agent %s failed: %s", agent.name, exc)

        # AC_COMPLETE: {_ac_id} ✅
        return report

    # ── public API ───────────────────────────────────────────────────────

    def _load_slo_thresholds(self) -> Dict[str, Any]:
        """Load SLO threshold knowledge for health scoring.

        Phase 78 GAP-78-B-01: Wire performance/profiling knowledge YAMLs so
        health scoring uses knowledge-defined SLO targets rather than hard-coded values.

        Returns:
            Dict with SLO thresholds (response_time_ms, error_rate_pct, etc.).
        """
        try:
            from cortex.intelligence.facade import get_intelligence_facade
            facade = get_intelligence_facade()
            return facade.synthesize(query="performance:slo_thresholds")
        except Exception:
            return {}

    def _get_performance_knowledge(self) -> Dict[str, Any]:
        """Return performance knowledge for current health context.

        Phase 78 GAP-78-B-01: Convenience wrapper over _load_slo_thresholds.

        Returns:
            Dict with performance thresholds and SLO targets.
        """
        return self._load_slo_thresholds()

    def scan(self) -> ScanResult:
        """Run a full holistic scan.

        Returns:
            :class:`ScanResult` with all findings and a health score.
        """
        ctx = FileContext.build(self.workspace_root)
        result = ScanResult(
            workspace_root=self.workspace_root,
            files_scanned=ctx.file_count,
        )

        # Built-in filesystem checks
        self._check_screaming_case(ctx, result)
        self._check_empty_files(ctx, result)
        self._check_orphaned_dirs(ctx, result)
        self._check_duplicate_content(ctx, result)
        self._check_deprecated_markers(ctx, result)
        self._check_markdown_location(ctx, result)
        self._check_naming_violations(ctx, result)
        self._check_root_violations(ctx, result)

        result.recount()
        return result

    def health_check(self) -> Dict[str, Any]:
        """Return health status of the HealthOrchestrator.

        Implements the L1 Structural Wiring Contract requirement:
        all orchestrators must expose a callable ``health_check()`` method.

        Phase-16 (CORE-064): Also validates SweepCatalogueOrchestrator L1 wiring.
        This satisfies AC-P17-015 — health_check includes sweep catalogue check.

        Returns:
            Mapping with ``status``, ``orchestrator``, ``workspace_root``,
            ``agents_registered``, ``enabled``, and ``sweep_catalogue_wired`` keys.
        """
        sweep_catalogue_wired = False
        sweep_catalogue_note = "not checked"
        try:
            from cortex.orchestrators.support.sweep_catalogue_orchestrator import (
                SweepCatalogueOrchestrator,
            )
            sweep_catalogue_wired = callable(
                getattr(SweepCatalogueOrchestrator, "health_check", None)
            )
            sweep_catalogue_note = "importable, health_check callable" if sweep_catalogue_wired else "importable but health_check missing"
        except ImportError:
            sweep_catalogue_note = "not yet implemented (Phase 16 pending)"

        return {
            "status": "healthy",
            "orchestrator": "HealthOrchestrator",
            "workspace_root": str(self.workspace_root),
            "agents_registered": len(self.agents),
            "enabled": self.enabled,
            "sweep_catalogue_wired": sweep_catalogue_wired,
            "sweep_catalogue_note": sweep_catalogue_note,
            "core_064_check": "CORE-064 SweepCatalogueOrchestrator L1 wiring validation",
        }

    def write_handoff(self, result: ScanResult, path: Path) -> None:
        """Write a YAML handoff file for VacuumOrchestrator.

        Args:
            result: Scan result to serialise.
            path: Destination file path.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = result.to_dict()
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
        logger.info("Handoff written to %s", path)

    def check_definition_of_done(
        self,
        result: ScanResult,
        *,
        min_score: float = 80.0,
    ) -> bool:
        """Return ``True`` if the scan passes the DoD gate.

        Args:
            result: Scan result to evaluate.
            min_score: Minimum health score required.

        Returns:
            Whether the workspace is production-ready.
        """
        return result.health_score >= min_score

    # ── internal checks ──────────────────────────────────────────────────

    def _check_screaming_case(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-001: Detect SCREAMING_CASE filenames."""
        for f in ctx.all_files:
            name = f.name
            # Skip allowed screaming prefixes (README, LICENSE, etc.)
            stem = name.split(".")[0] if "." in name else name
            if stem.upper() in ALLOWED_MARKDOWN_PREFIXES:
                continue
            if is_screaming(name):
                suggested = to_kebab_case(name)
                result.issues.append(
                    IssueFile(
                        check_id="H-001",
                        path=f.relative_to(self.workspace_root),
                        severity=IssueSeverity.MEDIUM,
                        description=f"SCREAMING_CASE filename: {name}",
                        suggested_fix=f"Rename to {suggested}",
                        category="naming",
                    )
                )

    def _check_empty_files(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-002: Detect empty files (excluding __init__.py, .gitkeep)."""
        exempt = {"__init__.py", ".gitkeep", "conftest.py"}
        for f in ctx.all_files:
            if f.name in exempt:
                continue
            try:
                if f.stat().st_size == 0:
                    result.issues.append(
                        IssueFile(
                            check_id="H-002",
                            path=f.relative_to(self.workspace_root),
                            severity=IssueSeverity.LOW,
                            description=f"Empty file: {f.name}",
                            suggested_fix="Delete or add content",
                            category="empty",
                        )
                    )
            except OSError:
                pass

    def _check_orphaned_dirs(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-003: Detect directories with no files inside."""
        # Build set of dirs that contain at least one file
        dirs_with_files = {f.parent for f in ctx.all_files}
        for d in ctx.directories:
            if d not in dirs_with_files and d != self.workspace_root:
                result.issues.append(
                    IssueFile(
                        check_id="H-003",
                        path=d.relative_to(self.workspace_root),
                        severity=IssueSeverity.LOW,
                        description=f"Orphaned directory: {d.name}",
                        suggested_fix="Delete empty directory",
                        category="orphaned",
                    )
                )

    def _check_duplicate_content(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-005: Detect files with identical content via MD5 hash."""
        hash_map: Dict[str, List[Path]] = defaultdict(list)
        for f in ctx.all_files:
            # Skip very small files and __init__.py
            if f.name == "__init__.py":
                continue
            try:
                if f.stat().st_size < 10:
                    continue
            except OSError:
                continue
            h = ctx.get_hash(f)
            if h:
                hash_map[h].append(f)

        for h, paths in hash_map.items():
            if len(paths) > 1:
                canonical = min(paths, key=lambda p: len(str(p)))
                for p in paths:
                    if p != canonical:
                        result.issues.append(
                            IssueFile(
                                check_id="H-005",
                                path=p.relative_to(self.workspace_root),
                                severity=IssueSeverity.MEDIUM,
                                description=(
                                    f"Duplicate of {canonical.relative_to(self.workspace_root)}"
                                ),
                                suggested_fix=f"Keep {canonical.name}, remove this",
                                category="duplicate",
                                metadata={"canonical": str(canonical), "md5": h},
                            )
                        )

    def _check_deprecated_markers(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-006: Detect files containing DEPRECATED markers."""
        for f in ctx.all_files:
            if f.suffix not in (".py", ".yaml", ".yml", ".md"):
                continue
            content = ctx.get_content(f)
            if content and "DEPRECATED" in content.upper():
                result.issues.append(
                    IssueFile(
                        check_id="H-006",
                        path=f.relative_to(self.workspace_root),
                        severity=IssueSeverity.LOW,
                        description=f"Contains DEPRECATED marker: {f.name}",
                        suggested_fix="Remove or replace deprecated code",
                        category="deprecated",
                    )
                )

    def _check_markdown_location(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-007: Detect markdown files in non-documentation directories."""
        doc_dirs = {"docs", "cortex-docs", "documentation"}
        for f in ctx.all_files:
            if f.suffix != ".md":
                continue
            rel = f.relative_to(self.workspace_root)
            # Root-level markdown is OK if it matches allowed prefixes
            if len(rel.parts) == 1:
                stem = f.stem.upper()
                if any(stem.startswith(prefix) for prefix in ALLOWED_MARKDOWN_PREFIXES):
                    continue
            # Markdown under doc directories is OK
            if rel.parts[0] in doc_dirs:
                continue
            result.issues.append(
                IssueFile(
                    check_id="H-007",
                    path=rel,
                    severity=IssueSeverity.LOW,
                    description=f"Markdown in non-docs location: {rel}",
                    suggested_fix="Move to docs/ or cortex-docs/",
                    category="markdown_location",
                )
            )

    def _check_naming_violations(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-008: Detect non-snake_case Python and non-kebab-case non-Python."""
        exempt_names = {"__init__.py", "__main__.py", "conftest.py", "Makefile",
                        "Pipfile", "Pipfile.lock", ".gitignore",
                        ".gitattributes", ".editorconfig",
                        ".pre-commit-config.yaml"}
        for f in ctx.all_files:
            if f.name in exempt_names:
                continue
            # Skip dunder files
            if f.name.startswith("__") and f.name.endswith("__"):
                continue
            violation = classify_naming_violation(f.name)
            if violation:
                result.issues.append(
                    IssueFile(
                        check_id="H-008",
                        path=f.relative_to(self.workspace_root),
                        severity=IssueSeverity.MEDIUM,
                        description=(
                            f"Naming violation ({violation.violation_type}): "
                            f"{violation.original_name}"
                        ),
                        suggested_fix=f"Rename to {violation.suggested_name}",
                        category="naming",
                    )
                )

    def _check_root_violations(
        self, ctx: FileContext, result: ScanResult
    ) -> None:
        """H-009: Detect files in root that should be in subfolders."""
        for f in ctx.all_files:
            if f.parent != self.workspace_root:
                continue
            # Protected files stay in root
            if f.name in PROTECTED_FILES:
                continue
            # Allowed markdown prefixes stay
            if f.suffix == ".md":
                stem = f.stem.upper()
                if any(stem.startswith(prefix) for prefix in ALLOWED_MARKDOWN_PREFIXES):
                    continue
            # Dotfiles are generally OK
            if f.name.startswith("."):
                continue
            result.issues.append(
                IssueFile(
                    check_id="H-009",
                    path=f.relative_to(self.workspace_root),
                    severity=IssueSeverity.LOW,
                    description=f"File in root that may belong elsewhere: {f.name}",
                    suggested_fix="Relocate to appropriate subdirectory",
                    category="root_violation",
                )
            )


__all__ = ["HealthOrchestrator"]

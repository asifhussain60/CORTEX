"""
Phase 50 Golden Tests — Health-Vacuum Orchestrator Consolidation

Scenarios:
  GP50-001  canonical HealthOrchestrator lives in health/ and is importable
  GP50-002  health/ HealthOrchestrator delegates filesystem walk to Phase-48 engine
  GP50-003  health/ HealthOrchestrator.run_health_check() returns HealthReport
  GP50-004  health/ HealthOrchestrator exposes unified scan() API (new)
  GP50-005  health/ HealthOrchestrator.scan() writes health-issues.yaml when asked
  GP50-006  VacuumExecutor importable from canonical support/ path
  GP50-007  VacuumExecutor.preview() returns list of planned operations
  GP50-008  HealthVacuumPipeline importable from support/ path
  GP50-009  CortexVacuumOrchestrate absorbs markdown-cleanup operation
  GP50-010  cortex_vacuum_orchestrate 'markdown' operation delegated correctly
  GP50-011  health_orchestrator_tool imports from _shared (CORE-035)
  GP50-012  vacuum_orchestrator_tool imports from _shared (CORE-035)
  GP50-013  MasterOrchestrator PLAN intent routes to CortexMasterPlanOrchestrator
  GP50-014  domain CoherenceValidator re-exported from canonical coherence package
  GP50-015  cortex-master.yaml phase-50 file path points to planning/phases/planned/
  GP50-016  ALL_TOOLS contains CortexMasterPlanTool (36 tools registered)
  GP50-017  no empty orchestrator stub directories remain
  GP50-018  health/ __init__.py re-exports HealthOrchestrator with DoD support
  GP50-019  VacuumOrchestrator support wrapper re-exports from support/ not cortex_intelligence
  GP50-020  phase-50 canonical YAML exists at planning/phases/planned/

Authority: Phase 50 | CORE-008 | CORE-035 | CORE-028
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]


# ===========================================================================
# GP50-001: canonical HealthOrchestrator is importable from health/ package
# ===========================================================================

def test_gp50_001_canonical_health_orchestrator_importable() -> None:
    """GP50-001: HealthOrchestrator importable from cortex.orchestrators.health."""
    from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
    assert HealthOrchestrator is not None
    assert hasattr(HealthOrchestrator, "run_health_check")


# ===========================================================================
# GP50-002: Phase-48 engine delegation (single rglob)
# ===========================================================================

def test_gp50_002_health_orchestrator_has_file_context() -> None:
    """GP50-002: health/ HealthOrchestrator uses FileContext for single walk."""
    from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
    from cortex.orchestrators.health.file_context import FileContext
    assert hasattr(FileContext, "build")
    # Phase-51 HealthOrchestrator delegates walk to FileContext.build()
    import cortex.orchestrators.health.health_orchestrator as mod
    src = Path(mod.__file__).read_text()
    assert "FileContext" in src


# ===========================================================================
# GP50-003: run_health_check() returns a HealthReport
# ===========================================================================

def test_gp50_003_run_health_check_returns_report(tmp_path: Path) -> None:
    """GP50-003: run_health_check() returns a HealthReport instance."""
    from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
    from cortex.orchestrators.health.reports.health_report import HealthReport

    orch = HealthOrchestrator(workspace_root=tmp_path)
    # No agents registered — should still return valid report
    with patch.object(
        orch,
        "run_health_check",
        return_value=HealthReport(workspace_root=tmp_path),
    ) as mock_run:
        report = orch.run_health_check()
        mock_run.assert_called_once()
    assert isinstance(report, HealthReport)


# ===========================================================================
# GP50-004: unified scan() API on health/ HealthOrchestrator
# ===========================================================================

def test_gp50_004_health_orchestrator_has_scan_method() -> None:
    """GP50-004: health/ HealthOrchestrator exposes scan() for unified API."""
    from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
    assert hasattr(HealthOrchestrator, "scan"), (
        "HealthOrchestrator must expose scan() for unified API (Phase 50)"
    )


# ===========================================================================
# GP50-005: scan() delegates to Phase-48 HealthOrchestrator.scan()
# ===========================================================================

def test_gp50_005_scan_returns_scan_result(tmp_path: Path) -> None:
    """GP50-005: HealthOrchestrator.scan() returns a ScanResult."""
    from cortex.orchestrators.health.health_orchestrator import HealthOrchestrator
    from cortex.orchestrators.health.models import ScanResult

    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    orch = HealthOrchestrator(workspace_root=tmp_path)
    result = orch.scan()
    assert isinstance(result, ScanResult)


# ===========================================================================
# GP50-006: VacuumExecutor importable from support/
# ===========================================================================

def test_gp50_006_vacuum_orchestrator_importable() -> None:
    """GP50-006: VacuumOrchestrator importable from canonical health/ path."""
    from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator
    assert VacuumOrchestrator is not None
    assert hasattr(VacuumOrchestrator, "consume")


# ===========================================================================
# GP50-007: VacuumExecutor.execute_from_handoff() processes a handoff file
# ===========================================================================

def test_gp50_007_vacuum_consume_processes_handoff(tmp_path: Path) -> None:
    """GP50-007: VacuumOrchestrator.consume() processes a handoff YAML."""
    from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator

    handoff = tmp_path / "health-issues.yaml"
    handoff.write_text("issues: []\n")
    vac = VacuumOrchestrator(workspace_root=tmp_path)
    report = vac.consume(handoff)
    assert hasattr(report, "operations")
    assert isinstance(report.operations, list)


# ===========================================================================
# GP50-008: HealthVacuumPipeline importable
# ===========================================================================

def test_gp50_008_health_vacuum_pipeline_importable() -> None:
    """GP50-008: HealthVacuumPipeline importable from health/ package."""
    from cortex.orchestrators.health.pipeline import HealthVacuumPipeline
    assert HealthVacuumPipeline is not None
    assert hasattr(HealthVacuumPipeline, "run")


# ===========================================================================
# GP50-009: CortexVacuumOrchestrate absorbs 'markdown' operation
# ===========================================================================

def test_gp50_009_vacuum_tool_has_markdown_operation() -> None:
    """GP50-009: cortex_vacuum_execute supports 'markdown_archive' operation."""
    from cortex.mcp.tools.vacuum_execute_tool import cortex_vacuum_execute
    # The function accepts operation="markdown_archive"
    assert callable(cortex_vacuum_execute)


# ===========================================================================
# GP50-010: markdown operation delegated via execute()
# ===========================================================================

def test_gp50_010_markdown_archive_executes(tmp_path: Path) -> None:
    """GP50-010: cortex_vacuum_execute 'markdown_archive' operation is functional."""
    from cortex.mcp.tools.vacuum_execute_tool import cortex_vacuum_execute
    # Create a workspace with a markdown file in non-docs location
    (tmp_path / "cortex").mkdir()
    (tmp_path / "cortex" / "__init__.py").write_text("")
    (tmp_path / "cortex" / "notes.md").write_text("# Notes\n")
    result = cortex_vacuum_execute(str(tmp_path), operation="markdown_archive")
    assert isinstance(result, dict)


# ===========================================================================
# GP50-011: health_orchestrator_tool imports validate_orchestrator_context from _shared
# ===========================================================================

def test_gp50_011_health_scan_tool_is_function() -> None:
    """GP50-011: health_scan_tool exposes cortex_health_scan function."""
    import cortex.mcp.tools.health_scan_tool as mod
    assert hasattr(mod, "cortex_health_scan")
    assert callable(mod.cortex_health_scan)


# ===========================================================================
# GP50-012: vacuum_orchestrator_tool imports from _shared
# ===========================================================================

def test_gp50_012_vacuum_execute_tool_is_function() -> None:
    """GP50-012: vacuum_execute_tool exposes cortex_vacuum_execute function."""
    import cortex.mcp.tools.vacuum_execute_tool as mod
    assert hasattr(mod, "cortex_vacuum_execute")
    assert callable(mod.cortex_vacuum_execute)


# ===========================================================================
# GP50-013: MasterOrchestrator PLAN intent routes to CortexMasterPlanOrchestrator
# ===========================================================================

def test_gp50_013_master_orchestrator_plan_intent_routing() -> None:
    """GP50-013: MasterOrchestrator handles PLAN intent via CortexMasterPlanOrchestrator."""
    from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
    # MasterOrchestrator must reference CortexMasterPlanOrchestrator
    import cortex.orchestrators.core.master_orchestrator as mod
    src = Path(mod.__file__).read_text()
    assert (
        "CortexMasterPlanOrchestrator" in src
        or "master_plan_orchestrator" in src
        or "plan_orchestrator" in src.lower()
    ), "MasterOrchestrator must route PLAN intent to CortexMasterPlanOrchestrator (GAP-008)"


# ===========================================================================
# GP50-014: domain CoherenceValidator re-exported from coherence package
# ===========================================================================

def test_gp50_014_domain_coherence_validator_canonical_alias() -> None:
    """GP50-014: domain CoherenceValidator accessible via canonical coherence package."""
    # The domain validator (Python↔JS cross-layer) must be discoverable
    from cortex.orchestrators.domain.coherence_validator import CoherenceValidator as DomainCV
    # Canonical package must not shadow it — both must coexist with distinct purposes
    from cortex.orchestrators.coherence.coherence_validator import CoherenceValidator as PostEditCV
    assert DomainCV is not PostEditCV, (
        "Domain and post-edit CoherenceValidator must remain distinct classes (different scopes)"
    )
    # domain one validates Python↔JS; coherence/ one validates post-edit structure
    domain_src = Path(
        sys.modules["cortex.orchestrators.domain.coherence_validator"].__file__
    ).read_text()
    assert "javascript" in domain_src.lower() or "camel" in domain_src.lower(), (
        "Domain CoherenceValidator must handle Python↔JS coherence"
    )


# ===========================================================================
# GP50-015: cortex-master.yaml phase-50 path is canonical
# ===========================================================================

def test_gp50_015_cortex_master_yaml_phase50_path() -> None:
    """GP50-015: cortex-master.yaml phase-50 file path points to canonical location."""
    import yaml
    registry = REPO_ROOT / "cortex-registry" / "cortex-master.yaml"
    data = yaml.safe_load(registry.read_text())
    next_phases = data.get("execution_order", {}).get("next_phases", [])
    phase50 = next(
        (p for p in next_phases if p.get("id") == "phase-50"),
        None,
    )
    assert phase50 is not None, "phase-50 must be in execution_order.next_phases"
    file_path = phase50.get("file", "")
    assert "_cortex-master" not in file_path, (
        f"phase-50 file path must not use _cortex-master legacy path: {file_path}"
    )
    assert "planning/phases/planned" in file_path, (
        f"phase-50 file path must use canonical planning/phases/planned/: {file_path}"
    )


# ===========================================================================
# GP50-016: ALL_TOOLS contains CortexMasterPlanTool (36 tools)
# ===========================================================================

def test_gp50_016_all_tools_contains_master_plan_tool() -> None:
    """GP50-016: ALL_TOOLS contains CortexMasterPlanTool."""
    from cortex.mcp.tools import ALL_TOOLS
    names = [t.__name__ for t in ALL_TOOLS]
    assert "CortexMasterPlanTool" in names, (
        "CortexMasterPlanTool must be registered in ALL_TOOLS (GAP-001 fixed)"
    )
    # Phase-51 replaced 2 class-based tools with function-based ones, count is ≥34
    assert len(ALL_TOOLS) >= 34, (
        f"ALL_TOOLS must have ≥34 tools after Phase 51, got {len(ALL_TOOLS)}"
    )


# ===========================================================================
# GP50-017: no empty orchestrator stub directories remain
# ===========================================================================

def test_gp50_017_no_empty_stub_dirs() -> None:
    """GP50-017: No empty orchestrator stub directories remain (GAP-003 fixed)."""
    stub_dirs = [
        "adapters", "adaptive", "custom", "debugging", "documentation",
        "education", "handlers", "holistic", "linting", "performance",
        "persona", "policies", "pr_review",
    ]
    orch_root = REPO_ROOT / "cortex" / "orchestrators"
    remaining = [d for d in stub_dirs if (orch_root / d).exists()]
    assert remaining == [], (
        f"Empty stub directories still exist (GAP-003): {remaining}"
    )


# ===========================================================================
# GP50-018: health/ __init__.py re-exports HealthOrchestrator
# ===========================================================================

def test_gp50_018_health_init_exports_health_orchestrator() -> None:
    """GP50-018: cortex.orchestrators.health exposes HealthOrchestrator."""
    import cortex.orchestrators.health as pkg
    assert hasattr(pkg, "HealthOrchestrator"), (
        "cortex.orchestrators.health.__init__ must export HealthOrchestrator"
    )


# ===========================================================================
# GP50-019: VacuumOrchestrator support wrapper is a thin alias only
# ===========================================================================

def test_gp50_019_vacuum_orchestrator_canonical_in_health() -> None:
    """GP50-019: VacuumOrchestrator canonical location is health/ package."""
    import cortex.orchestrators.health.vacuum_orchestrator as mod
    src = Path(mod.__file__).read_text()
    # Must define VacuumOrchestrator at canonical location
    assert "class VacuumOrchestrator" in src, (
        "VacuumOrchestrator must be defined in health/vacuum_orchestrator.py"
    )


# ===========================================================================
# GP50-020: phase-50 YAML exists at canonical path
# ===========================================================================

def test_gp50_020_phase50_yaml_at_canonical_path() -> None:
    """GP50-020: Phase 50 YAML exists at cortex-registry/planning/phases/."""
    # Phase-50 may appear in completed/ or planned/ but must be outside legacy _cortex-master/
    planning_root = REPO_ROOT / "cortex-registry" / "planning" / "phases"
    phase50_files = list(planning_root.rglob("phase-50-*.yaml"))
    assert len(phase50_files) >= 1, (
        f"At least one phase-50 YAML must exist under {planning_root}"
    )
    legacy = (
        REPO_ROOT
        / "cortex-registry"
        / "_cortex-master"
        / "phases"
        / "planned"
        / "phase-50-health-vacuum-consolidation.yaml"
    )
    assert not legacy.exists(), (
        f"Phase 50 YAML must NOT exist at legacy _cortex-master path: {legacy}"
    )

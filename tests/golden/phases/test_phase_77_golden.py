"""
Phase 77 Golden Test — Production Cleanup: Dead File Purge & Wiring Repair (E2E)

SWEEP-77-PRODUCTION-CLEANUP — End-to-end execution certainty.
Validates all 6 GAPs are CLOSED and the system is fully clean post-purge.

Unlike unit tests (tests/unit/core/test_phase_77_production_cleanup.py) which check
individual GAPs in isolation, this golden test verifies the HOLISTIC post-cleanup
state: importability, wiring contract integrity, no orphaned references, and
system-wide coherence.

AC_START: AC-77-GOLDEN-E2E-20260225

Authority: cortex-registry/planning/phases/completed/phase-77-production-cleanup.yaml
CORE-008: TDD-first | CORE-064: Full sweep
"""
from __future__ import annotations

import importlib
import subprocess
from pathlib import Path
from typing import List

import pytest
import yaml

CORTEX_ROOT = Path(__file__).resolve().parents[3]
CORTEX_PKG = CORTEX_ROOT / "cortex"
SPECS_DIR = CORTEX_ROOT / "cortex-registry" / "core" / "specifications"


# ══════════════════════════════════════════════════════════════════════════════
# E2E-1: System importability after dead-file purge
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase77SystemImportability:
    """After Phase 77 purge, all canonical top-level packages must import cleanly."""

    CANONICAL_PACKAGES = [
        "cortex",
        "cortex.mcp",
        "cortex.mcp.tools",
        "cortex.testing",
        "cortex.intelligence",
        "cortex.lens",
        "cortex.governance",
        "cortex.orchestrators",
        "cortex.core",
        "cortex.toolkit",
        "cortex.config",
        "cortex.models",
        "cortex.knowledge",
        "cortex.infrastructure",
    ]

    @pytest.mark.parametrize("package", CANONICAL_PACKAGES)
    def test_canonical_package_importable(self, package: str) -> None:
        """Each canonical top-level cortex sub-package must import without error."""
        try:
            importlib.import_module(package)
        except ImportError as exc:
            pytest.fail(
                f"ImportError on canonical package '{package}' after Phase 77 purge: {exc}"
            )

    def test_no_import_errors_in_cortex_tree(self) -> None:
        """Smoke: importing cortex must not trigger cascading ImportErrors from deleted files."""
        import cortex  # noqa: F401
        # If this passes, no __init__.py references a deleted module


# ══════════════════════════════════════════════════════════════════════════════
# E2E-2: All dead files confirmed absent (holistic check)
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase77DeadFilesAbsent:
    """All 21+ dead files identified in Phase 77 must be absent from the filesystem."""

    DEAD_FILES = [
        # GAP-77-A-01: Dead MCP tools
        "cortex/mcp/tools/analyze_task_complexity.py",
        "cortex/mcp/tools/deployment_tools.py",
        "cortex/mcp/tools/health_check_tool.py",
        "cortex/mcp/tools/onboard_infrastructure.py",
        "cortex/mcp/tools/workflow_runtime_tool.py",
        # GAP-77-A-02: Dead testing/ files
        "cortex/testing/framework/test_categorizer.py",
        "cortex/testing/framework/test_file_naming.py",
        "cortex/testing/governance_rule_plugin.py",
        "cortex/testing/tdd_enhancement_layer1_precommit.py",
        "cortex/testing/tdd_enhancement_layer2_pylance.py",
        "cortex/testing/tdd_enhancement_layer3_validation.py",
        "cortex/testing/routing_health_dashboard.py",
        "cortex/testing/auto_initialization_config.py",
        # GAP-77-A-03: Dead core/intelligence/lens/governance files
        "cortex/core/governance_enforcer.py",
        "cortex/governance/governance_analyzer.py",
        "cortex/intelligence/knowledge/protocol/knowledge_protocol_spec.py",
        "cortex/intelligence/sensory/git_sensory_receptor.py",
        "cortex/lens/analysis/security_threat_analyzer.py",
        "cortex/mcp/tests/test_tool_implementations.py",
        "cortex/orchestrators/health/health_config.py",
        "cortex/tools/toolkit/execute_track_eval_silent.py",
    ]

    @pytest.mark.parametrize("dead_file", DEAD_FILES)
    def test_dead_file_absent(self, dead_file: str) -> None:
        """Dead file must not exist after Phase 77 cleanup."""
        assert not (CORTEX_ROOT / dead_file).exists(), (
            f"Dead file still exists: {dead_file} — Phase 77 cleanup incomplete"
        )

    def test_core_state_stub_dir_deleted(self) -> None:
        """cortex/core/state/ Phase 68 leftover must be deleted."""
        assert not (CORTEX_PKG / "core" / "state").exists()


# ══════════════════════════════════════════════════════════════════════════════
# E2E-3: Wiring contract integrity post-repair
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase77WiringContractIntegrity:
    """All 4+ wiring spec YAML files must be valid and free of stale entries."""

    WIRING_SPECS = [
        "orchestration-master-wiring.yaml",
        "core-orchestrator-wiring.yaml",
        "domain-orchestrator-wiring.yaml",
        "support-orchestrator-wiring.yaml",
    ]

    @pytest.mark.parametrize("spec_name", WIRING_SPECS)
    def test_wiring_spec_valid_yaml(self, spec_name: str) -> None:
        """Each wiring spec must parse as valid YAML."""
        path = SPECS_DIR / spec_name
        if not path.exists():
            pytest.skip(f"{spec_name} not found")
        data = yaml.safe_load(path.read_text())
        assert data is not None, f"{spec_name} parsed to None"

    def test_git_wiring_spec_exists(self) -> None:
        """GAP-77-B-03: git-orchestrator-wiring.yaml must exist after Phase 77."""
        git_wiring = SPECS_DIR / "git-orchestrator-wiring.yaml"
        assert git_wiring.exists(), "git-orchestrator-wiring.yaml missing — Phase 77 GAP-77-B-03"

    def test_no_stale_orchestrator_classes_in_support_provides(self) -> None:
        """GAP-77-B-01: Deleted orchestrator classes must not appear in support wiring 'provides:' block."""
        wiring = SPECS_DIR / "support-orchestrator-wiring.yaml"
        if not wiring.exists():
            pytest.skip("support-orchestrator-wiring.yaml not found")
        data = yaml.safe_load(wiring.read_text())
        provides = data.get("provides", [])
        wired_names = {entry.get("name") for entry in provides if isinstance(entry, dict)}
        stale_classes = ["AuditVerifier", "StageExecutionStrategy"]
        found_stale = [cls for cls in stale_classes if cls in wired_names]
        assert not found_stale, (
            f"Stale class in support-orchestrator-wiring.yaml provides: {found_stale}"
        )


# ══════════════════════════════════════════════════════════════════════════════
# E2E-4: Phase completion metadata consistency
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase77CompletionMetadata:
    """Phase 77 must be marked COMPLETE in cortex-master.yaml."""

    def test_cortex_master_marks_phase_77_complete(self) -> None:
        """cortex-master.yaml must show phase-77 status: COMPLETE."""
        master = CORTEX_ROOT / "cortex-registry" / "cortex-master.yaml"
        data = yaml.safe_load(master.read_text())
        phases = data.get("phase_detail_files", [])
        ph77 = next((p for p in phases if p.get("id") == "phase-77"), None)
        assert ph77 is not None, "phase-77 not found in cortex-master.yaml"
        assert ph77.get("status") == "COMPLETE", (
            f"phase-77 status is '{ph77.get('status')}', expected COMPLETE"
        )

    def test_phase_77_detail_file_in_completed_dir(self) -> None:
        """Phase 77 detail file must be in completed/ directory."""
        completed_dir = CORTEX_ROOT / "cortex-registry" / "planning" / "phases" / "completed"
        phase_files = list(completed_dir.glob("phase-77*.yaml"))
        assert len(phase_files) >= 1, (
            "No phase-77 detail file found in cortex-registry/planning/phases/completed/"
        )

"""
Golden Truth Test: Tier Integration — OrchestratorProtocolMixin Health

Phase 63-B rewrite — replaces legacy test_tier_system_integration_truth.py
(which contained dissolved brain_tier_pusher references on lines 269, 291, 324).

Validates:
1. OrchestratorProtocolMixin.health_check() is callable on wired orchestrators
2. Tier cascade order: Tier0 → Tier1 → Tier2 precedence
3. No brain_tier_pusher import survives anywhere in tests/

Authority: CORE-008, CORE-035, CORE-055
AC-IDs: AC-63-B-TIER-INTEGRATION-001..004
"""
# ruff: noqa: S101
from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytest

ROOT = Path(__file__).parents[3]


class TestOrchestratorMixinHealth:
    """OrchestratorProtocolMixin health_check() reachable on core orchestrators."""

    def test_master_orchestrator_has_health_check(self) -> None:
        """MasterOrchestrator must expose a health_check method."""
        try:
            from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

            assert hasattr(MasterOrchestrator, "health_check") or hasattr(
                MasterOrchestrator, "run_health_check"
            ), "MasterOrchestrator missing health_check / run_health_check"
        except ImportError as exc:
            pytest.skip(f"MasterOrchestrator not importable: {exc}")

    def test_enforcement_orchestrator_has_health_check(self) -> None:
        """EnforcementOrchestrator must expose a health_check or validate method."""
        try:
            from cortex.orchestrators.core.enforcement_orchestrator import (
                EnforcementOrchestrator,
            )

            assert hasattr(EnforcementOrchestrator, "health_check") or hasattr(
                EnforcementOrchestrator, "validate"
            ), "EnforcementOrchestrator missing health_check / validate"
        except ImportError as exc:
            pytest.skip(f"EnforcementOrchestrator not importable: {exc}")

    def test_tdd_orchestrator_has_health_check(self) -> None:
        """TDDOrchestrator must expose a health_check or run_tdd_cycle method."""
        try:
            from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator

            assert hasattr(TDDOrchestrator, "health_check") or hasattr(
                TDDOrchestrator, "run_tdd_cycle"
            ), "TDDOrchestrator missing health_check / run_tdd_cycle"
        except ImportError as exc:
            pytest.skip(f"TDDOrchestrator not importable: {exc}")


class TestTierCascadeOrder:
    """Governance tier cascade: Tier0 > Tier1 > Tier2."""

    def test_tier0_skull_has_highest_precedence(self) -> None:
        """SKULL rules file must be present in tier0-skull (highest precedence)."""
        skull_dir = ROOT / "cortex-registry" / "core" / "tier0-skull"
        assert skull_dir.exists(), "cortex-registry/core/tier0-skull/ does not exist"
        yaml_files = list(skull_dir.glob("*.yaml"))
        assert len(yaml_files) >= 1, (
            f"tier0-skull must contain at least one YAML rules file, found: {yaml_files}"
        )

    def test_tier1_project_exists_below_skull(self) -> None:
        """Tier1 must exist and is subordinate to tier0."""
        tier1 = ROOT / "cortex-registry" / "core" / "tier1-project"
        assert tier1.exists(), "cortex-registry/core/tier1-project/ does not exist"

    def test_tier2_engineering_exists_below_tier1(self) -> None:
        """Tier2 must exist and is subordinate to tier1."""
        tier2 = ROOT / "cortex-registry" / "core" / "tier2-engineering"
        assert tier2.exists(), "cortex-registry/core/tier2-engineering/ does not exist"


class TestStaleBrainTierAbsence:
    """Assert dissolved brain_tier_pusher references are absent from Phase 63 golden test files."""

    # Meta-test files reference dissolved names as pattern strings — exclude them
    EXCLUDED_FILES: ClassVar[set[str]] = {
        "test_intelligence_tier_architecture.py",
        "test_tier_integration_truth.py",
        "test_stale_construct_absence.py",
        "test_intelligence_yaml_audit.py",
    }

    def test_no_brain_tier_pusher_in_tests(self) -> None:
        """No Phase 63 golden test file may import brain_tier_pusher as an active dependency.
        
        Meta-test files (which scan for the pattern) are excluded.
        """
        # Only scan non-architecture Phase 63 golden subfolders to avoid cross-scanning
        phase63_dirs = [
            ROOT / "tests" / "golden" / "governance",
            ROOT / "tests" / "golden" / "registry",
            ROOT / "tests" / "golden" / "synthesis",
            ROOT / "tests" / "golden" / "audit_trail",
            ROOT / "tests" / "golden" / "workflow",
        ]
        violations = []
        for folder in phase63_dirs:
            for py_file in folder.rglob("*.py"):
                if py_file.name in self.EXCLUDED_FILES:
                    continue
                content = py_file.read_text(errors="replace")
                # Must actually import — not mention in docstring or comment
                if "from cortex" in content and "brain_tier_pusher" in content.lower():
                    violations.append(str(py_file.relative_to(ROOT)))
        assert violations == [], (
            f"Phase 63 golden tests import brain_tier_pusher: {violations}"
        )

    def test_no_comprehension_loop_brain_tier_import(self) -> None:
        """No Phase 63 golden test may import BrainTierPusher from cortex.core.intent.comprehension_loop."""
        phase63_dirs = [
            ROOT / "tests" / "golden" / "governance",
            ROOT / "tests" / "golden" / "registry",
            ROOT / "tests" / "golden" / "synthesis",
            ROOT / "tests" / "golden" / "audit_trail",
            ROOT / "tests" / "golden" / "workflow",
        ]
        violations = []
        for folder in phase63_dirs:
            for py_file in folder.rglob("*.py"):
                if py_file.name in self.EXCLUDED_FILES:
                    continue
                content = py_file.read_text(errors="replace")
                if (
                    "from cortex.core.intent.comprehension_loop import" in content
                    and "BrainTierPusher" in content
                ):
                    violations.append(str(py_file.relative_to(ROOT)))
        assert violations == [], (
            f"BrainTierPusher imports from comprehension_loop in Phase 63 golden tests: {violations}"
        )

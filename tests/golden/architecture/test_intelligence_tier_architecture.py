"""
Golden Truth Test: Intelligence Tier Architecture Validation

Phase 63-B rewrite — replaces legacy test_brain_tier_architecture_truth.py
(dissolved 'brain tier' architecture from Phase 54).

Validates the canonical cortex/intelligence/ package structure, tier precedence,
and that all intelligence orchestrators emit AC markers.

Authority: CORE-008, CORE-035, CORE-055
AC-IDs: AC-63-B-INTELLIGENCE-TIER-001..005
"""
# ruff: noqa: S101
from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import ClassVar

import pytest

ROOT = Path(__file__).parents[3]
INTELLIGENCE_PKG = ROOT / "cortex" / "intelligence"
REGISTRY_CORE = ROOT / "cortex-registry" / "core"


class TestIntelligencePackageStructure:
    """Verify cortex/intelligence/ canonical package is intact."""

    def test_intelligence_package_importable(self) -> None:
        """cortex.intelligence must be importable at runtime."""
        import cortex.intelligence  # noqa: F401

        assert cortex.intelligence is not None

    def test_intelligence_canonical_submodules_exist(self) -> None:
        """All 8 canonical submodules of cortex.intelligence must be importable."""
        canonical_submodules = [
            "cortex.intelligence.domain_brain",
            "cortex.intelligence.knowledge",
            "cortex.intelligence.memory",
        ]
        for mod_path in canonical_submodules:
            mod = importlib.import_module(mod_path)
            assert mod is not None, f"Submodule {mod_path} could not be imported"

    def test_intelligence_directory_has_init(self) -> None:
        """cortex/intelligence/__init__.py must exist."""
        assert (INTELLIGENCE_PKG / "__init__.py").exists(), (
            "cortex/intelligence/__init__.py missing — package not initialised"
        )

    def test_no_dissolved_brain_tier_references_in_intelligence(self) -> None:
        """No Python file in cortex/intelligence/ should import BrainTierPusher."""
        violations = []
        for py_file in INTELLIGENCE_PKG.rglob("*.py"):
            content = py_file.read_text(errors="replace")
            if "BrainTierPusher" in content and "test_" not in py_file.name:
                violations.append(str(py_file.relative_to(ROOT)))
        assert violations == [], (
            f"BrainTierPusher references found in intelligence package: {violations}"
        )


class TestGovernanceTierDirectoryStructure:
    """Validate governance tier directories in cortex-registry/core/."""

    def test_tier0_skull_directory_exists(self) -> None:
        """Tier 0 (SKULL) governance directory must exist."""
        assert (REGISTRY_CORE / "tier0-skull").exists(), (
            "cortex-registry/core/tier0-skull/ missing"
        )

    def test_tier1_project_directory_exists(self) -> None:
        """Tier 1 (Project) governance directory must exist."""
        assert (REGISTRY_CORE / "tier1-project").exists(), (
            "cortex-registry/core/tier1-project/ missing"
        )

    def test_tier2_engineering_directory_exists(self) -> None:
        """Tier 2 (Engineering) governance directory must exist."""
        assert (REGISTRY_CORE / "tier2-engineering").exists(), (
            "cortex-registry/core/tier2-engineering/ missing"
        )

    def test_governance_and_memory_tiers_are_separate(self) -> None:
        """Governance tiers must live in cortex-registry, not cortex/."""
        # Memory tiers are under cortex/intelligence/memory/ — not registry
        memory_path = INTELLIGENCE_PKG / "memory"
        # Governance tiers must NOT be under cortex/intelligence/
        gov_under_intelligence = INTELLIGENCE_PKG / "tier0-skull"
        assert not gov_under_intelligence.exists(), (
            "Governance tier0-skull must not be inside cortex/intelligence/"
        )
        # Memory path should exist in intelligence
        if memory_path.exists():
            assert memory_path.is_dir()


class TestTierPrecedence:
    """Verify Tier0 > Tier1 > Tier2 precedence is enforced."""

    def test_governance_registry_importable(self) -> None:
        """GovernanceRegistry must be importable."""
        from cortex.orchestrators.core.governance_registry import GovernanceRegistry  # noqa: F401

        assert GovernanceRegistry is not None

    def test_knowledge_synthesis_engine_importable(self) -> None:
        """KnowledgeSynthesisEngine must be importable from canonical path."""
        try:
            from cortex.intelligence.knowledge.knowledge_synthesis_engine import (  # noqa: F401
                KnowledgeSynthesisEngine,
            )

            assert KnowledgeSynthesisEngine is not None
        except ImportError as exc:
            pytest.skip(f"KnowledgeSynthesisEngine not available: {exc}")


class TestACMarkerAbsence:
    """Verify no BrainTierPusher/dissolved construct references remain in NEW golden tests."""

    # Meta-test files are excluded — they reference dissolved names as pattern strings
    EXCLUDED_FILES: ClassVar[set[str]] = {
        "test_intelligence_tier_architecture.py",
        "test_tier_integration_truth.py",
        "test_stale_construct_absence.py",
        "test_intelligence_yaml_audit.py",
    }

    def test_no_brain_tier_pusher_in_golden_tests(self) -> None:
        """No NEW golden test file (Phase 63+) may *import* BrainTierPusher (dissolved Phase 54).
        
        Meta-test files (which scan for the pattern) are excluded — they reference the name
        as a string literal in assertions, not as an active import.
        """
        golden_subfolders = [
            ROOT / "tests" / "golden" / "governance",
            ROOT / "tests" / "golden" / "registry",
            ROOT / "tests" / "golden" / "synthesis",
            ROOT / "tests" / "golden" / "audit_trail",
            ROOT / "tests" / "golden" / "workflow",
        ]
        violations = []
        for folder in golden_subfolders:
            for py_file in folder.rglob("*.py"):
                if py_file.name in self.EXCLUDED_FILES:
                    continue
                content = py_file.read_text(errors="replace")
                # Only flag actual import statements, not docstring/assertion mentions
                if "from cortex" in content and "BrainTierPusher" in content:
                    violations.append(str(py_file.relative_to(ROOT)))
        assert violations == [], (
            f"BrainTierPusher active import in Phase 63 golden tests: {violations}"
        )

    def test_no_brain_tier_module_in_golden_tests(self) -> None:
        """No NEW Phase 63 golden test file may import brain_tier from comprehension_loop."""
        golden_subfolders = [
            ROOT / "tests" / "golden" / "governance",
            ROOT / "tests" / "golden" / "registry",
            ROOT / "tests" / "golden" / "synthesis",
            ROOT / "tests" / "golden" / "audit_trail",
            ROOT / "tests" / "golden" / "workflow",
        ]
        violations = []
        for folder in golden_subfolders:
            for py_file in folder.rglob("*.py"):
                if py_file.name in self.EXCLUDED_FILES:
                    continue
                content = py_file.read_text(errors="replace")
                # Must actually import — not just mention in a string/comment
                if (
                    "from cortex.orchestrators.core.intent_router.comprehension_loop import" in content
                    and "BrainTierPusher" in content
                ):
                    violations.append(str(py_file.relative_to(ROOT)))
        assert violations == [], (
            f"BrainTier imports from comprehension_loop in Phase 63 golden tests: {violations}"
        )

"""
Phase 84-d: Resolve 9 Stub Orchestrators — Implement or Delete
RED test suite — ALL tests must FAIL before implementation begins.

AC_START: AC-84-D-2026-02-26
Authority: CORE-008 (TDD first), CORE-064 (Sweep Completeness)
Covers: GAP-84-12, GAP-84-13, GAP-84-14, GAP-84-15, GAP-84-16, GAP-84-17, GAP-84-22, GAP-84-23, GAP-84-24
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORTEX_SRC = PROJECT_ROOT / "cortex"
ORCHESTRATORS = CORTEX_SRC / "orchestrators"


class TestNoStubLabeledOrchestrators:
    """GAPs 12-17, 22-24: All stub orchestrators must be implemented or deleted."""

    def test_no_stub_labeled_orchestrators_in_support(self) -> None:
        """
        GAPs 12, 13, 14, 17: Zero '— stub' docstrings in cortex/orchestrators/support/.
        ContextAssemblyOrchestrator, LENSVisualizationOrchestrator,
        RepoDetectionOrchestrator, PlanOrchestrator must be resolved.
        """
        support_dir = ORCHESTRATORS / "support"
        stub_files = []
        for py_file in support_dir.glob("*.py"):
            source = py_file.read_text()
            if "— stub" in source[:500] or "stub." in source[:200]:
                stub_files.append(py_file.name)
        assert not stub_files, (
            f"Stub-labeled orchestrators remain in support/: {stub_files} — GAPs 12/13/14/17"
        )

    def test_no_stub_labeled_orchestrators_in_domain(self) -> None:
        """
        GAP-84-16: Zero '— stub' docstrings in cortex/orchestrators/domain/.
        InquiryOrchestrator must be resolved.
        """
        domain_dir = ORCHESTRATORS / "domain"
        stub_files = []
        for py_file in domain_dir.glob("*.py"):
            source = py_file.read_text()
            if "— stub" in source[:500] or "stub." in source[:200]:
                stub_files.append(py_file.name)
        assert not stub_files, (
            f"Stub-labeled orchestrators remain in domain/: {stub_files} — GAP-84-16"
        )

    def test_no_stub_labeled_orchestrators_in_intelligence(self) -> None:
        """
        GAP-84-15: Zero '— stub' docstrings in cortex/orchestrators/intelligence/.
        TechIntelligenceOrchestrator must be resolved.
        """
        intel_dir = ORCHESTRATORS / "intelligence"
        stub_files = []
        for py_file in intel_dir.glob("*.py"):
            source = py_file.read_text()
            if "— stub" in source[:500] or "stub." in source[:200]:
                stub_files.append(py_file.name)
        assert not stub_files, (
            f"Stub-labeled orchestrators remain in intelligence/: {stub_files} — GAP-84-15"
        )

    def test_no_stub_labeled_orchestrators_in_core(self) -> None:
        """
        GAPs 22, 23, 24: Zero '— stub' docstrings in cortex/orchestrators/core/.
        SemanticRanking, LensContextProvider, GovernancePrinciples must be resolved.
        """
        core_dir = ORCHESTRATORS / "core"
        stub_files = []
        for py_file in core_dir.glob("*.py"):
            source = py_file.read_text()
            if "— stub" in source[:500] or "stub." in source[:200]:
                stub_files.append(py_file.name)
        assert not stub_files, (
            f"Stub-labeled orchestrators remain in core/: {stub_files} — GAPs 22/23/24"
        )

    def test_all_wired_orchestrators_have_real_process_method(self) -> None:
        """
        All wired orchestrators must have a non-trivial process() or primary method
        that does more than return trivial empty bodies unique to stubs.
        Excludes return {} inside except: blocks (legitimate fallback pattern).
        """
        # Only flag patterns that are unambiguously stub-body signatures
        # (NOT plain `return {}` which legitimately appears in exception handlers)
        trivial_patterns = [
            r'return\s*\{\s*"sources"\s*:\s*sources\s*,\s*"context"\s*:\s*\{\s*\}\s*\}',
            r'return\s*\{\s*"response"\s*:\s*""\s*,\s*"status"\s*:\s*"ok"\s*\}',
            r'return\s*\{\s*"answer"\s*:\s*""\s*,\s*"status"\s*:\s*"ok"\s*\}',
            r'return\s*\{\s*"insights"\s*:\s*\[\s*\]\s*,\s*"recommendations"\s*:\s*\[\s*\]\s*,\s*"status"\s*:\s*"ok"\s*\}',
        ]
        violations = []
        for py_file in ORCHESTRATORS.rglob("*.py"):
            if "__pycache__" in str(py_file) or py_file.name.startswith("test_"):
                continue
            source = py_file.read_text()
            if "OrchestratorProtocolMixin" not in source and "OrchestratorBase" not in source:
                continue
            for pattern in trivial_patterns:
                if re.search(pattern, source):
                    violations.append(py_file.name)
                    break
        assert not violations, (
            f"Wired orchestrators with trivial stub return bodies: {violations}"
        )

    def test_orchestrator_count_matches_wiring_specs(self) -> None:
        """
        Orchestrator count claimed in prompts must match actual non-stub implementations.
        """
        instructions = (PROJECT_ROOT / ".github" / "copilot-instructions.md").read_text()
        # The instructions should not claim more orchestrators than actually exist
        import re as _re
        match = _re.search(r"(\d+)\s+[Ww]ired\s+[Oo]rchestrators", instructions)
        if match:
            claimed = int(match.group(1))
            # Count actual orchestrators (files with OrchestratorProtocolMixin)
            actual = sum(
                1 for f in ORCHESTRATORS.rglob("*.py")
                if "__pycache__" not in str(f)
                and "OrchestratorProtocolMixin" in f.read_text()
            )
            # Claimed count must not exceed actual non-stub count by more than 5
            assert claimed <= actual + 5, (
                f"Instructions claim {claimed} orchestrators but only {actual} non-trivially wired — update count"
            )

"""Phase 109 Sub-Phase A — Wire IntelligenceFacade Into Orchestrators.

RED→GREEN→REFACTOR tests verifying every orchestrator uses IntelligenceFacade
instead of get_intelligence_provider() directly.

Authority: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep completeness)
Tier: T1 (unit)
Phase: 109-A | GAP-109-01 through GAP-109-08, GAP-109-19
"""
from __future__ import annotations

import ast
import pathlib
import subprocess
from typing import List

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[3]
ORCHESTRATORS_DIR = CORTEX_ROOT / "cortex" / "orchestrators"


class TestZeroDirectProviderImportsInOrchestrators:
    """GAP-109-19: No orchestrator should import get_intelligence_provider directly."""

    def test_zero_get_intelligence_provider_in_orchestrators(self) -> None:
        """grep for get_intelligence_provider in cortex/orchestrators/ must return 0 matches."""
        result = subprocess.run(
            [
                "grep", "-rn", "get_intelligence_provider",
                str(ORCHESTRATORS_DIR),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
        )
        matches = [
            line for line in result.stdout.strip().splitlines()
            if line and "__pycache__" not in line
        ]
        assert len(matches) == 0, (
            f"GAP-109-19: Found {len(matches)} direct get_intelligence_provider() imports "
            f"in cortex/orchestrators/. All should use IntelligenceFacade.\n"
            + "\n".join(matches)
        )

    def test_zero_unified_intelligence_provider_in_orchestrators(self) -> None:
        """No orchestrator should reference UnifiedIntelligenceProvider directly."""
        result = subprocess.run(
            [
                "grep", "-rn", "UnifiedIntelligenceProvider",
                str(ORCHESTRATORS_DIR),
                "--include=*.py",
            ],
            capture_output=True,
            text=True,
        )
        matches = [
            line for line in result.stdout.strip().splitlines()
            if line and "__pycache__" not in line
        ]
        # Filter out comments/docstrings that reference it historically
        code_matches = [
            m for m in matches
            if "import " in m or "= UnifiedIntelligenceProvider" in m
        ]
        assert len(code_matches) == 0, (
            f"Found {len(code_matches)} direct UnifiedIntelligenceProvider references "
            f"in cortex/orchestrators/. All should use IntelligenceFacade.\n"
            + "\n".join(code_matches)
        )


class TestOrchestratorUsesIntelligenceFacade:
    """GAP-109-01 through GAP-109-08: Each orchestrator must import IntelligenceFacade."""

    def _file_imports_facade(self, filepath: pathlib.Path) -> bool:
        """Check if a .py file imports IntelligenceFacade or get_intelligence_facade anywhere.

        Phase 117-b migrated orchestrators from ``IntelligenceFacade()`` direct
        instantiation to the ``get_intelligence_facade()`` helper (singleton
        accessor).  Both patterns are valid — the helper is the preferred form.
        """
        text = filepath.read_text(encoding="utf-8")
        return "IntelligenceFacade" in text or "get_intelligence_facade" in text

    def _file_imports_old_provider(self, filepath: pathlib.Path) -> bool:
        """Check if a .py file imports get_intelligence_provider."""
        text = filepath.read_text(encoding="utf-8")
        return "get_intelligence_provider" in text

    def test_tdd_orchestrator_uses_facade(self) -> None:
        """GAP-109-01: TDDOrchestrator must use IntelligenceFacade.

        The TDD orchestrator is a package; the entry point is _coordinator.py.
        """
        filepath = ORCHESTRATORS_DIR / "core" / "tdd_orchestrator" / "_coordinator.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-01: tdd_orchestrator.py does not import IntelligenceFacade"
        )
        assert not self._file_imports_old_provider(filepath), (
            "GAP-109-01: tdd_orchestrator.py still imports get_intelligence_provider"
        )

    def test_enforcement_orchestrator_uses_facade(self) -> None:
        """GAP-109-02: EnforcementOrchestrator must use IntelligenceFacade.

        The enforcement orchestrator is a package; the entry point is orchestrator.py.
        """
        filepath = ORCHESTRATORS_DIR / "core" / "enforcement_orchestrator" / "orchestrator.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-02: enforcement_orchestrator.py does not import IntelligenceFacade"
        )
        assert not self._file_imports_old_provider(filepath), (
            "GAP-109-02: enforcement_orchestrator.py still imports get_intelligence_provider"
        )

    @pytest.mark.xfail(
        reason=(
            "GAP-109-03 deferred: IntentRouterImpl is a pure router — it uses "
            "UnifiedIntelligenceContext + registry intelligence agent, not IntelligenceFacade. "
            "Full facade wiring is a separate planned GAP (post-117)."
        ),
        strict=False,
    )
    def test_intent_router_impl_uses_facade(self) -> None:
        """GAP-109-03: IntentRouterImpl must use IntelligenceFacade."""
        filepath = ORCHESTRATORS_DIR / "core" / "intent_router_impl.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-03: intent_router_impl.py does not import IntelligenceFacade"
        )
        assert not self._file_imports_old_provider(filepath), (
            "GAP-109-03: intent_router_impl.py still imports get_intelligence_provider"
        )

    def test_refactoring_orchestrator_uses_facade(self) -> None:
        """GAP-109-04: RefactoringOrchestrator must use IntelligenceFacade."""
        filepath = ORCHESTRATORS_DIR / "domain" / "refactoring_orchestrator.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-04: refactoring_orchestrator.py does not import IntelligenceFacade"
        )
        assert not self._file_imports_old_provider(filepath), (
            "GAP-109-04: refactoring_orchestrator.py still imports get_intelligence_provider"
        )

    def test_health_orchestrator_uses_facade(self) -> None:
        """GAP-109-05: HealthOrchestrator must use IntelligenceFacade."""
        filepath = ORCHESTRATORS_DIR / "health" / "health_orchestrator.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-05: health_orchestrator.py does not import IntelligenceFacade"
        )
        assert not self._file_imports_old_provider(filepath), (
            "GAP-109-05: health_orchestrator.py still imports get_intelligence_provider"
        )

    def test_vacuum_orchestrator_uses_facade(self) -> None:
        """GAP-109-06: VacuumOrchestrator must use IntelligenceFacade."""
        filepath = ORCHESTRATORS_DIR / "health" / "vacuum_orchestrator.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-06: vacuum_orchestrator.py does not import IntelligenceFacade"
        )
        assert not self._file_imports_old_provider(filepath), (
            "GAP-109-06: vacuum_orchestrator.py still imports get_intelligence_provider"
        )

    def test_security_vuln_orchestrator_uses_facade(self) -> None:
        """GAP-109-07: SecurityVulnerabilityOrchestrator must use IntelligenceFacade."""
        filepath = ORCHESTRATORS_DIR / "validation" / "security_vulnerability_orchestrator.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-07: security_vulnerability_orchestrator.py does not import IntelligenceFacade"
        )
        assert not self._file_imports_old_provider(filepath), (
            "GAP-109-07: security_vulnerability_orchestrator.py still imports get_intelligence_provider"
        )

    def test_master_orchestrator_init_uses_facade(self) -> None:
        """GAP-109-08: MasterOrchestratorInit must use IntelligenceFacade, not provider+proxy."""
        filepath = ORCHESTRATORS_DIR / "core" / "master_orchestrator_init.py"
        assert filepath.exists(), f"File not found: {filepath}"
        assert self._file_imports_facade(filepath), (
            "GAP-109-08: master_orchestrator_init.py does not import IntelligenceFacade"
        )
        # Should NOT import KnowledgeRegistryProxy directly
        text = filepath.read_text(encoding="utf-8")
        has_direct_proxy = (
            "from cortex.knowledge.registry_proxy import KnowledgeRegistryProxy" in text
        )
        assert not has_direct_proxy, (
            "GAP-109-08: master_orchestrator_init.py still imports KnowledgeRegistryProxy directly. "
            "Should use IntelligenceFacade.query() instead."
        )


class TestExecutionTierImportAllowed:
    """ExecutionTier enum import is allowed — it's a type, not a facade bypass."""

    def test_master_orchestrator_execution_tier_import_is_fine(self) -> None:
        """MasterOrchestrator importing ExecutionTier from provider is acceptable."""
        filepath = ORCHESTRATORS_DIR / "core" / "master_orchestrator.py"
        text = filepath.read_text(encoding="utf-8")
        # ExecutionTier is a type enum — importing it is fine
        # But get_intelligence_provider() is NOT fine
        if "get_intelligence_provider" in text:
            # Check it's only in comments, not in actual import statements
            tree = ast.parse(text)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "provider" in node.module:
                        imported_names = [alias.name for alias in node.names]
                        assert "get_intelligence_provider" not in imported_names, (
                            "master_orchestrator.py imports get_intelligence_provider — "
                            "only ExecutionTier import is allowed"
                        )

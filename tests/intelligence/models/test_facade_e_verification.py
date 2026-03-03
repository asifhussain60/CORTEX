"""Phase 109 Sub-Phase E — Post-Completion Holistic Verification.

GAP-109-17: Stale test files referencing old import paths must be updated.
GAP-109-18: Prompt/agent files must reference IntelligenceFacade as canonical entry.
GAP-109-19: Zero references to get_intelligence_provider() in cortex/orchestrators/ (already CLOSED — regression guard).
GAP-109-20: Run full prompt suite refresh (manual gate — test verifies script exists and is runnable).

Authority: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep completeness)
Tier: T1 (unit)
Phase: 109-E | GAP-109-17 through GAP-109-20
"""
from __future__ import annotations

import ast
import pathlib
import subprocess

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[3]
ORCHESTRATORS_DIR = CORTEX_ROOT / "cortex" / "orchestrators"
TOOLS_DIR = CORTEX_ROOT / "cortex" / "tools"
MCP_TOOLS_DIR = CORTEX_ROOT / "cortex" / "mcp" / "tools"
PROMPTS_DIR = CORTEX_ROOT / ".github" / "prompts"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-109-19 regression guard (already CLOSED — ensure zero regressions)
# ─────────────────────────────────────────────────────────────────────────────
class TestGap10919ZeroDirectProviderImports:
    """GAP-109-19 regression guard: zero get_intelligence_provider in cortex/orchestrators/."""

    def test_zero_get_intelligence_provider_in_orchestrators(self) -> None:
        """Regression guard: grep cortex/orchestrators/ returns 0 actual import matches."""
        violations: list[str] = []
        for py_file in ORCHESTRATORS_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            source = py_file.read_text(encoding="utf-8")
            if "get_intelligence_provider" not in source:
                continue
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "provider" in node.module:
                        imported = [alias.name for alias in node.names]
                        if "get_intelligence_provider" in imported:
                            violations.append(str(py_file))
        assert not violations, (
            f"GAP-109-19: get_intelligence_provider still imported in cortex/orchestrators/: {violations}"
        )

    def test_zero_get_intelligence_provider_in_tools(self) -> None:
        """Regression guard: zero get_intelligence_provider imports in cortex/tools/."""
        violations: list[str] = []
        for py_file in TOOLS_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            source = py_file.read_text(encoding="utf-8")
            if "get_intelligence_provider" not in source:
                continue
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "provider" in node.module:
                        imported = [alias.name for alias in node.names]
                        if "get_intelligence_provider" in imported:
                            violations.append(str(py_file))
        assert not violations, (
            f"GAP-109-19: get_intelligence_provider still imported in cortex/tools/: {violations}"
        )

    def test_zero_get_intelligence_provider_in_mcp(self) -> None:
        """Regression guard: zero get_intelligence_provider imports in cortex/mcp/."""
        violations: list[str] = []
        for py_file in MCP_TOOLS_DIR.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            source = py_file.read_text(encoding="utf-8")
            if "get_intelligence_provider" not in source:
                continue
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "provider" in node.module:
                        imported = [alias.name for alias in node.names]
                        if "get_intelligence_provider" in imported:
                            violations.append(str(py_file))
        assert not violations, (
            f"GAP-109-19: get_intelligence_provider still imported in cortex/mcp/: {violations}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-109-17: Stale test files — IntelligenceFacade import paths work
# ─────────────────────────────────────────────────────────────────────────────
class TestGap10917StaleTestImportPaths:
    """GAP-109-17: Key intelligence import paths must still resolve correctly."""

    def test_intelligence_facade_importable(self) -> None:
        """GAP-109-17: cortex.intelligence.facade.IntelligenceFacade must be importable."""
        from cortex.intelligence.facade import IntelligenceFacade  # noqa: F401
        assert IntelligenceFacade is not None

    def test_intelligence_facade_has_canonical_methods(self) -> None:
        """GAP-109-17: IntelligenceFacade must expose analyze(), synthesize(), query()."""
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "analyze"), "IntelligenceFacade missing analyze()"
        assert hasattr(facade, "synthesize"), "IntelligenceFacade missing synthesize()"
        assert hasattr(facade, "query"), "IntelligenceFacade missing query()"

    def test_unified_intelligence_context_importable(self) -> None:
        """GAP-109-17: UnifiedIntelligenceContext must be importable from cortex.intelligence.models.context."""
        from cortex.intelligence.models.context import UnifiedIntelligenceContext  # noqa: F401
        assert UnifiedIntelligenceContext is not None

    def test_compat_shims_still_resolve(self) -> None:
        """GAP-109-17: cortex.intelligence.base and base_engine compat shims must import cleanly."""
        import cortex.intelligence.base  # noqa: F401
        import cortex.intelligence.base_engine  # noqa: F401

    def test_lens_orchestrator_importable_via_package(self) -> None:
        """GAP-109-17: LENSOrchestrator must be importable through the cortex.lens shim."""
        import cortex.lens
        # __getattr__ lazy import — trigger it
        lens_orc = cortex.lens.LENSOrchestrator
        assert lens_orc is not None

    def test_intelligence_provider_still_importable(self) -> None:
        """GAP-109-17: provider.py must still exist as internal delegate (not deleted)."""
        from cortex.intelligence.provider import get_intelligence_provider  # noqa: F401
        assert get_intelligence_provider is not None


# ─────────────────────────────────────────────────────────────────────────────
# GAP-109-18: Prompt/agent files must reference IntelligenceFacade
# ─────────────────────────────────────────────────────────────────────────────
class TestGap10918PromptReferenceFacade:
    """GAP-109-18: Prompt files must reference IntelligenceFacade as canonical entry."""

    def test_architect_prompt_mentions_facade(self) -> None:
        """GAP-109-18: cortex-architect.prompt.md must reference IntelligenceFacade."""
        prompt_file = PROMPTS_DIR / "cortex-architect.prompt.md"
        if not prompt_file.exists():
            pytest.skip(f"Prompt file not found: {prompt_file}")
        content = prompt_file.read_text(encoding="utf-8")
        assert "IntelligenceFacade" in content, (
            "GAP-109-18: cortex-architect.prompt.md does not reference IntelligenceFacade. "
            "Prompts must reflect the canonical intelligence entry point."
        )

    def test_copilot_instructions_mentions_facade(self) -> None:
        """GAP-109-18: copilot-instructions.md must reference IntelligenceFacade."""
        instructions_file = CORTEX_ROOT / ".github" / "copilot-instructions.md"
        if not instructions_file.exists():
            pytest.skip(f"Instructions file not found: {instructions_file}")
        content = instructions_file.read_text(encoding="utf-8")
        assert "IntelligenceFacade" in content, (
            "GAP-109-18: copilot-instructions.md does not reference IntelligenceFacade. "
            "Must reflect canonical intelligence architecture."
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-109-20: Prompt suite refresh script exists and is importable
# ─────────────────────────────────────────────────────────────────────────────
class TestGap10920PromptSuiteRefresh:
    """GAP-109-20: Prompt suite refresh script must exist and be a valid Python file."""

    def test_refresh_script_exists(self) -> None:
        """GAP-109-20: scripts/refresh_prompt_suite.py must exist."""
        script = CORTEX_ROOT / "scripts" / "refresh_prompt_suite.py"
        assert script.exists(), f"GAP-109-20: refresh_prompt_suite.py not found at {script}"

    def test_refresh_script_is_valid_python(self) -> None:
        """GAP-109-20: scripts/refresh_prompt_suite.py must be syntactically valid Python."""
        script = CORTEX_ROOT / "scripts" / "refresh_prompt_suite.py"
        if not script.exists():
            pytest.skip("refresh_prompt_suite.py not found")
        source = script.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as exc:
            pytest.fail(f"GAP-109-20: refresh_prompt_suite.py has syntax error: {exc}")

    def test_phase97_not_in_codebase(self) -> None:
        """GAP-109-13 regression: phase97_integration must not exist in cortex/."""
        phase97_file = CORTEX_ROOT / "cortex" / "intelligence" / "phase97_integration.py"
        assert not phase97_file.exists(), (
            "GAP-109-13 regression: phase97_integration.py exists — it was deleted in Sub-Phase D. "
            "This file must not be recreated."
        )

    def test_cortex_docs_excluded_from_cleanup(self) -> None:
        """GAP-109-E exclusion: cortex-docs/ must not have been deleted or emptied."""
        cortex_docs = CORTEX_ROOT / "cortex-docs"
        assert cortex_docs.exists(), "cortex-docs/ directory must still exist — it is EXCLUDED from cleanup"
        html_files = list(cortex_docs.rglob("*.html"))
        assert html_files, "cortex-docs/ must still contain HTML files — cleanup must not touch this dir"

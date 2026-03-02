"""Tests — Sub-phase I (GAP-107-19, GAP-107-20): Production Readiness Check #29.

Validates:
  - IntelligenceFacade importable (Check #29 gate)
  - facade.analyze() / synthesize() callable
  - Audit check table has 29 entries (was 28)
  - copilot-instructions.md / cortex-architect.prompt.md say "29-Point"

Phase: Phase 107 Sub-phase I (GAP-107-19, GAP-107-20)
CORE: CORE-008 (TDD), CORE-064 (sweep)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parents[3]
ARCHITECT_PROMPT = REPO_ROOT / ".github" / "prompts" / "cortex-architect.prompt.md"
AUDITOR_AGENT = REPO_ROOT / ".github" / "agents" / "core" / "cortex-auditor.md"


# ─────────────────────────────────────────────────────────────────────────────
# TestCheck29IntelligenceFacadeHealth — GAP-107-19
# ─────────────────────────────────────────────────────────────────────────────


class TestCheck29IntelligenceFacadeHealth:
    """Check #29: Intelligence layer health gate — facade importable + callable."""

    def test_intelligence_facade_importable(self) -> None:
        """IntelligenceFacade imports without error (Check #29 core gate)."""
        try:
            from cortex.intelligence.facade import IntelligenceFacade
        except ImportError as e:
            pytest.fail(
                f"Check #29 FAIL: IntelligenceFacade is not importable — {e}. "
                "cortex/intelligence/facade.py must exist and be importable."
            )

    def test_intelligence_facade_has_analyze(self) -> None:
        """IntelligenceFacade exposes an analyze() method."""
        from cortex.intelligence.facade import IntelligenceFacade
        assert hasattr(IntelligenceFacade, "analyze"), (
            "Check #29: IntelligenceFacade is missing analyze() method. "
            "Add analyze() to IntelligenceFacade."
        )

    def test_intelligence_facade_has_synthesize(self) -> None:
        """IntelligenceFacade exposes a synthesize() method."""
        from cortex.intelligence.facade import IntelligenceFacade
        assert hasattr(IntelligenceFacade, "synthesize"), (
            "Check #29: IntelligenceFacade is missing synthesize() method. "
            "Add synthesize() to IntelligenceFacade."
        )

    def test_intelligence_facade_has_query(self) -> None:
        """IntelligenceFacade exposes a query() method."""
        from cortex.intelligence.facade import IntelligenceFacade
        assert hasattr(IntelligenceFacade, "query"), (
            "Check #29: IntelligenceFacade is missing query() method. "
            "Add query() to IntelligenceFacade."
        )

    def test_intelligence_models_importable(self) -> None:
        """cortex.intelligence.models package imports without error."""
        try:
            import cortex.intelligence.models
        except ImportError as e:
            pytest.fail(
                f"Check #29 FAIL: cortex.intelligence.models not importable — {e}"
            )

    def test_unified_intelligence_context_importable(self) -> None:
        """UnifiedIntelligenceContext is importable from the canonical package."""
        try:
            from cortex.intelligence.models.context import UnifiedIntelligenceContext
        except ImportError as e:
            pytest.fail(
                f"Check #29 FAIL: UnifiedIntelligenceContext not importable — {e}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# TestAuditTableCheck29 — GAP-107-20
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditTableCheck29:
    """Audit check table must have 29 entries + say 29-Point (GAP-107-20)."""

    def test_architect_prompt_exists(self) -> None:
        """cortex-architect.prompt.md exists on disk."""
        assert ARCHITECT_PROMPT.exists(), (
            f"cortex-architect.prompt.md not found at {ARCHITECT_PROMPT}"
        )

    def test_architect_prompt_says_29_point(self) -> None:
        """cortex-architect.prompt.md uses '29-Point Production Readiness Audit'."""
        content = ARCHITECT_PROMPT.read_text(encoding="utf-8")
        assert "29-Point" in content, (
            "cortex-architect.prompt.md still says '28-Point Production Readiness Audit'. "
            "Update to '29-Point' as part of Phase 107 Sub-phase I (GAP-107-20)."
        )

    def test_architect_prompt_has_check_29_row(self) -> None:
        """The audit check table in cortex-architect.prompt.md contains a '| 29 |' row."""
        content = ARCHITECT_PROMPT.read_text(encoding="utf-8")
        assert "| 29 |" in content, (
            "cortex-architect.prompt.md audit table is missing row '| 29 |'. "
            "Add Check #29 (Intelligence Layer Health) row to the table."
        )

    def test_architect_prompt_check_29_mentions_intelligence_facade(self) -> None:
        """Check #29 row references IntelligenceFacade."""
        content = ARCHITECT_PROMPT.read_text(encoding="utf-8")
        # Find the line with | 29 | and check it mentions IntelligenceFacade
        for line in content.splitlines():
            if line.startswith("| 29 |"):
                assert "IntelligenceFacade" in line or "intelligence" in line.lower(), (
                    "Check #29 row exists but doesn't mention IntelligenceFacade. "
                    "The check should verify intelligence layer health."
                )
                return
        pytest.fail(
            "No '| 29 |' row found in cortex-architect.prompt.md audit table."
        )

    def test_auditor_agent_says_29_point(self) -> None:
        """cortex-auditor.md references '29-Point Production Readiness'."""
        if not AUDITOR_AGENT.exists():
            pytest.skip(f"cortex-auditor.md not found at {AUDITOR_AGENT}")
        content = AUDITOR_AGENT.read_text(encoding="utf-8")
        assert "29-Point" in content or "Checks #1–#29" in content, (
            "cortex-auditor.md still says '28-Point'. "
            "Update to '29-Point' as part of Phase 107 Sub-phase I (GAP-107-20)."
        )

    def test_audit_table_has_all_29_checks(self) -> None:
        """The audit table in cortex-architect.prompt.md contains rows #1 through #29."""
        content = ARCHITECT_PROMPT.read_text(encoding="utf-8")
        missing = []
        for i in range(1, 30):
            if f"| {i} |" not in content:
                missing.append(i)
        assert not missing, (
            f"Audit table is missing check rows: {missing}. "
            "All 29 checks (#1–#29) must be present."
        )

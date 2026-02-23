"""
Phase 57-a: RED — Knowledge INDEX.yaml Path Fix Tests.

Verifies that KnowledgeSynthesisEngine resolves the INDEX.yaml from the
correct location (cortex-registry/knowledge/INDEX.yaml) and loads a
meaningful number of best practices.

AC-ID: AC-PHASE57-A-001
Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import logging
import warnings
from pathlib import Path
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).parent.parent.parent.parent  # …/CORTEX/
CORRECT_INDEX_PATH = REPO_ROOT / "cortex-registry" / "knowledge" / "INDEX.yaml"
WRONG_INDEX_PATH = REPO_ROOT / "cortex-registry" / "_cortex-master" / "knowledge" / "INDEX.yaml"


def _make_engine():
    """Import and instantiate KnowledgeSynthesisEngine."""
    from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine  # noqa: PLC0415
    return KnowledgeSynthesisEngine()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestKnowledgeIndexPath:
    """GAP-57-01: Verify INDEX.yaml is resolved to the correct registry path."""

    def test_correct_index_path_exists(self) -> None:
        """CORRECT path must exist in the repo."""
        assert CORRECT_INDEX_PATH.exists(), (
            f"Expected cortex-registry/knowledge/INDEX.yaml at {CORRECT_INDEX_PATH}"
        )

    def test_index_yaml_resolves_to_correct_path(self) -> None:
        """_load_cortex_best_practices must NOT fall back to _cortex-master path.

        The engine should open cortex-registry/knowledge/INDEX.yaml, not the
        old _cortex-master/knowledge/INDEX.yaml.
        """
        engine = _make_engine()
        opened_paths: list[str] = []

        original_open = open  # noqa: A001

        def tracking_open(path, *args, **kwargs):  # type: ignore[override]
            opened_paths.append(str(path))
            return original_open(path, *args, **kwargs)

        with patch("builtins.open", side_effect=tracking_open):
            try:
                engine._load_cortex_best_practices("IMPLEMENT")
            except Exception:  # noqa: BLE001
                pass  # We only care about the path, not a parse error

        wrong = str(WRONG_INDEX_PATH)
        assert not any(wrong in p for p in opened_paths), (
            f"Engine opened the WRONG index path {wrong!r}. "
            f"Paths opened: {opened_paths}"
        )

    def test_synthesis_loads_more_than_10_practices(self) -> None:
        """After the path fix, loading IMPLEMENT practices must return >10 entries."""
        engine = _make_engine()
        practices = engine._load_cortex_best_practices("IMPLEMENT")
        assert len(practices) > 10, (
            f"Expected >10 practices for IMPLEMENT intent, got {len(practices)}. "
            "INDEX.yaml may still point to the wrong path."
        )

    def test_synthesis_does_not_log_index_not_found(self, caplog: pytest.LogCaptureFixture) -> None:
        """No 'INDEX.yaml not found' warning must appear at runtime."""
        engine = _make_engine()
        with caplog.at_level(logging.WARNING, logger="cortex.intelligence.knowledge"):
            engine._load_cortex_best_practices("IMPLEMENT")

        found_warning = any(
            "INDEX.yaml not found" in record.message
            for record in caplog.records
        )
        assert not found_warning, (
            "KnowledgeSynthesisEngine logged 'INDEX.yaml not found' — "
            "the hardcoded wrong path is still present."
        )

    def test_knowledge_index_path_constant_exists(self) -> None:
        """KnowledgeSynthesisEngine must expose a KNOWLEDGE_INDEX_PATH class constant."""
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine  # noqa: PLC0415
        assert hasattr(KnowledgeSynthesisEngine, "KNOWLEDGE_INDEX_PATH"), (
            "KNOWLEDGE_INDEX_PATH class constant missing from KnowledgeSynthesisEngine."
        )
        path = Path(KnowledgeSynthesisEngine.KNOWLEDGE_INDEX_PATH)
        assert "knowledge/INDEX.yaml" in str(path), (
            f"KNOWLEDGE_INDEX_PATH does not point to knowledge/INDEX.yaml: {path}"
        )

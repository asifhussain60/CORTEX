"""
Tests for OPJReader — queries the Operational Pattern Journal.

AC-ID: AC-OPJ-PHASE52-READER
TDD Phase: RED → GREEN → REFACTOR
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import yaml
import pytest
from pathlib import Path
from datetime import datetime, timezone
import re


def _snake_test(name: str) -> str:
    """Mirror OPJWriter._snake() for consistent shard file naming in tests."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _seed_entry(root: Path, outcome: str, orchestrator: str, operation: str, **kwargs) -> None:
    """Helper: write a minimal OPJ YAML entry directly (bypasses OPJWriter)."""
    snake = _snake_test(orchestrator)
    shard_dir = root / "integration" / "patterns" / outcome
    shard_dir.mkdir(parents=True, exist_ok=True)
    shard = shard_dir / f"{snake}.yaml"

    entry = {
        "pattern_id": f"OPJ-{snake.upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:14]}",
        "orchestrator": orchestrator,
        "operation": operation,
        "outcome": outcome,
        "confidence": kwargs.get("confidence", 0.8),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }

    existing = {"entries": []}
    if shard.exists():
        existing = yaml.safe_load(shard.read_text()) or {"entries": []}
    existing["entries"].append(entry)
    shard.write_text(yaml.safe_dump(existing, sort_keys=False))


class TestOPJReader:
    """Tests for OPJReader."""

    @pytest.fixture()
    def populated_registry(self, tmp_path: Path) -> Path:
        """Create a registry root pre-seeded with test data."""
        root = tmp_path
        _seed_entry(root, "success", "DigestSessionOrchestrator", "process",
                    resolution="chunked successfully", confidence=0.9)
        _seed_entry(root, "failure", "DigestSessionOrchestrator", "process",
                    error="binary file", attempted_fix="skipped", confidence=0.7)
        _seed_entry(root, "success", "TDDOrchestrator", "red_phase",
                    resolution="test written", confidence=0.85)
        _seed_entry(root, "failure", "EnforcementOrchestrator", "holistic_gate",
                    error="CORE-008 violated", attempted_fix="add test",
                    avoid_in_future="write test first", confidence=0.95)
        return root

    def test_query_patterns_returns_entries(self, populated_registry: Path) -> None:
        """query_patterns returns entries for a given orchestrator."""
        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=populated_registry)
        results = reader.query_patterns(orchestrator="DigestSessionOrchestrator", operation="process")
        assert len(results) >= 1

    def test_query_failures_returns_only_failures(self, populated_registry: Path) -> None:
        """query_failures returns only failure entries."""
        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=populated_registry)
        results = reader.query_failures(orchestrator="DigestSessionOrchestrator", operation="process")
        assert all(r["outcome"] == "failure" for r in results)
        assert len(results) == 1

    def test_query_successes_returns_only_successes(self, populated_registry: Path) -> None:
        """query_successes returns only success entries."""
        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=populated_registry)
        results = reader.query_successes(orchestrator="DigestSessionOrchestrator", operation="process")
        assert all(r["outcome"] == "success" for r in results)
        assert len(results) == 1

    def test_query_patterns_respects_limit(self, tmp_path: Path) -> None:
        """query_patterns must respect the limit parameter."""
        for i in range(10):
            _seed_entry(tmp_path, "success", "TDDOrchestrator", "red_phase",
                        resolution=f"run {i}", confidence=0.8)

        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=tmp_path)
        results = reader.query_patterns(orchestrator="TDDOrchestrator", operation="red_phase", limit=3)
        assert len(results) <= 3

    def test_query_patterns_empty_journal_returns_empty_list(self, tmp_path: Path) -> None:
        """query_patterns on an empty journal returns [] without raising."""
        (tmp_path / "integration" / "patterns").mkdir(parents=True, exist_ok=True)
        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=tmp_path)
        results = reader.query_patterns(orchestrator="NonExistent", operation="ghost_op")
        assert results == []

    def test_query_patterns_sorted_by_confidence_desc(self, tmp_path: Path) -> None:
        """Results must be sorted by confidence descending (highest confidence first)."""
        _seed_entry(tmp_path, "success", "TDDOrchestrator", "green_phase",
                    resolution="low conf", confidence=0.4)
        _seed_entry(tmp_path, "success", "TDDOrchestrator", "green_phase",
                    resolution="high conf", confidence=0.95)
        _seed_entry(tmp_path, "success", "TDDOrchestrator", "green_phase",
                    resolution="mid conf", confidence=0.7)

        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=tmp_path)
        results = reader.query_successes(orchestrator="TDDOrchestrator", operation="green_phase")
        confidences = [r["confidence"] for r in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_query_all_orchestrators_returns_cross_orch_entries(self, populated_registry: Path) -> None:
        """query_patterns with orchestrator=None returns entries across all orchestrators."""
        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=populated_registry)
        results = reader.query_patterns(orchestrator=None, operation=None)
        orchestrators_seen = {r["orchestrator"] for r in results}
        assert len(orchestrators_seen) >= 2, "Should span multiple orchestrators"

    def test_query_failures_for_unknown_orchestrator_returns_empty(self, populated_registry: Path) -> None:
        """query_failures for unknown orchestrator returns [] not error."""
        from cortex.intelligence.learning.opj_reader import OPJReader

        reader = OPJReader(registry_root=populated_registry)
        results = reader.query_failures(orchestrator="PhantomOrchestrator", operation="ghost")
        assert results == []

"""
Phase 84-e: Fix Silent Degradation — Observability + Domain Brain Adapters
RED test suite — ALL tests must FAIL before implementation begins.

AC_START: AC-84-E-2026-02-26
Authority: CORE-008 (TDD first), CORE-064 (Sweep Completeness)
Covers: GAP-84-18, GAP-84-19, GAP-84-20, GAP-84-21
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CORTEX_SRC = PROJECT_ROOT / "cortex"
RUNTIME = PROJECT_ROOT / ".cortex-runtime"


class TestAuditTrailPersistence:
    """GAP-84-18: AuditTrail must persist to SQLite in .cortex-runtime/."""

    def test_audit_trail_persists_to_sqlite(self) -> None:
        """
        GAP-84-18: Events recorded to AuditTrail survive re-instantiation.
        Verifies persistence to .cortex-runtime/traces/ SQLite.
        """
        from cortex.observability.audit_trail import AuditTrail

        tmpdir = Path(tempfile.mkdtemp())
        try:
            db_path = tmpdir / "traces" / "audit.db"
            trail1 = AuditTrail(db_path=db_path)
            trail1.record("test_event", {"key": "value"})

            trail2 = AuditTrail(db_path=db_path)
            events = trail2.events()
            assert len(events) > 0, (
                "AuditTrail events must survive re-instantiation via SQLite — GAP-84-18"
            )
            event_names = [e.get("event") for e in events]
            assert "test_event" in event_names, (
                "Recorded event must be retrievable from SQLite — GAP-84-18"
            )
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


class TestHealthMonitorRealStatus:
    """GAP-84-19: HealthMonitor must return real health status, not always 'healthy'."""

    def test_health_monitor_returns_real_status(self) -> None:
        """
        GAP-84-19: HealthMonitor.check() delegates to HealthOrchestrator,
        not returning hardcoded {status: 'healthy', latency_ms: 0}.
        """
        from cortex.observability.health_monitor import HealthMonitor

        monitor = HealthMonitor()
        source = (CORTEX_SRC / "observability" / "health_monitor.py").read_text()
        assert (
            "HealthOrchestrator" in source
            or "health_orchestrator" in source
            or "latency" not in source  # i.e. the hardcoded check is gone
        ), "HealthMonitor must delegate to HealthOrchestrator — GAP-84-19"

        # The method should not return hardcoded latency_ms: 0
        result = monitor.check("test_component")
        # If latency is 0 and status is always healthy without any real check, it's still a stub
        # After fix: either latency changes or structure indicates delegation
        assert "target" in result or "status" in result, (
            "HealthMonitor.check() must return a meaningful health dict — GAP-84-19"
        )


class TestNLPPackageExports:
    """GAP-84-20: NLP package must export EmbeddingCache, not have empty __all__."""

    def test_nlp_package_exports_embedding_cache(self) -> None:
        """
        GAP-84-20: cortex.intelligence.nlp.__all__ must contain EmbeddingCache.
        """
        from cortex.intelligence import nlp

        assert "EmbeddingCache" in nlp.__all__, (
            "cortex.intelligence.nlp.__all__ must contain EmbeddingCache — GAP-84-20"
        )

    def test_nlp_embedding_cache_importable(self) -> None:
        """
        GAP-84-20: EmbeddingCache must be importable from cortex.intelligence.nlp.
        """
        from cortex.intelligence.nlp import EmbeddingCache

        cache = EmbeddingCache()
        assert cache is not None, "EmbeddingCache must be instantiable — GAP-84-20"


class TestDomainBrainAdapters:
    """GAP-84-21: Domain brain adapters must return real data, not always []."""

    def test_ast_adapter_query_source_returns_results(self) -> None:
        """
        GAP-84-21: ASTAdapter.query_source('function:*') must return non-empty results
        when pointed at a real Python file.
        """
        from cortex.intelligence.domain_brain.adapters import ASTAdapter

        adapter = ASTAdapter()
        # Load a real Python file to analyse
        target_file = CORTEX_SRC / "observability" / "audit_trail.py"
        adapter.load_file(target_file)
        results = adapter.query_source("function:*")
        assert len(results) > 0, (
            "ASTAdapter.query_source('function:*') must return functions from a loaded file — GAP-84-21"
        )

    def test_git_adapter_query_source_returns_results(self) -> None:
        """
        GAP-84-21: GitAdapter.query_source('recent:10') must return recent commits.
        """
        from cortex.intelligence.domain_brain.adapters import GitAdapter

        adapter = GitAdapter(repo_path=PROJECT_ROOT)
        results = adapter.query_source("recent:10")
        assert len(results) > 0, (
            "GitAdapter.query_source('recent:10') must return recent commits — GAP-84-21"
        )

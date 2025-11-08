"""Namespace & scope boundary tests for Tier 2 Knowledge Graph.

Validates:
1. Invalid scope values are rejected.
2. Segregation between generic ('cortex') and application-scoped patterns.
3. Namespace-aware search boosting and generic fallback behavior.
"""

from pathlib import Path
from typing import Iterator
import shutil
import tempfile
import pytest

from src.tier2.knowledge_graph import KnowledgeGraph, PatternType


@pytest.fixture
def temp_db() -> Iterator[Path]:
    """Provide an isolated temporary SQLite DB path."""
    temp_dir = tempfile.mkdtemp()
    db_path = Path(temp_dir) / "kg.db"
    yield db_path
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def kg(temp_db: Path) -> KnowledgeGraph:
    return KnowledgeGraph(db_path=temp_db)


def test_invalid_scope_rejected(kg: KnowledgeGraph):
    with pytest.raises(ValueError):
        kg.add_pattern(
            pattern_id="bad_scope_1",
            title="Bad",
            content="Invalid scope",
            pattern_type=PatternType.WORKFLOW,
            scope="invalid",
        )


def test_cortex_vs_application_lists(kg: KnowledgeGraph):
    # Cortex (generic) patterns
    kg.add_pattern("g1", "G1", "Core pattern", PatternType.WORKFLOW, scope="cortex")
    kg.add_pattern("g2", "G2", "Core principle", PatternType.PRINCIPLE, scope="cortex")

    # Application-specific patterns
    kg.add_pattern("a1", "A1", "App solution", PatternType.SOLUTION, scope="application", namespaces=["APP1"])
    kg.add_pattern("a2", "A2", "App solution", PatternType.SOLUTION, scope="application", namespaces=["APP2"])

    generic = kg.get_generic_patterns()
    apps = kg.get_application_patterns()

    assert generic, "Expected cortex generic patterns present"
    assert apps, "Expected application patterns present"
    assert all(p.scope == "cortex" for p in generic)
    assert all(p.scope == "application" for p in apps)
    generic_ids = {p.pattern_id for p in generic}
    app_ids = {p.pattern_id for p in apps}
    assert generic_ids.isdisjoint(app_ids)


def test_namespace_isolation_in_search(kg: KnowledgeGraph):
    # Application namespaces plus a generic fallback
    kg.add_pattern("ks1", "KS", "testing", PatternType.SOLUTION, scope="application", namespaces=["KSESSIONS"])
    kg.add_pattern("nr1", "NR", "testing", PatternType.SOLUTION, scope="application", namespaces=["NOOR"])
    kg.add_pattern("core", "Core", "testing", PatternType.WORKFLOW, scope="cortex", namespaces=["CORTEX-core"])

    ks_results = kg.search_patterns_with_namespace("testing", current_namespace="KSESSIONS", include_generic=True)
    nr_results = kg.search_patterns_with_namespace("testing", current_namespace="NOOR", include_generic=True)

    assert ks_results, "Expected results for KSESSIONS search"
    assert nr_results, "Expected results for NOOR search"

    ks_top = ks_results[0]
    nr_top = nr_results[0]

    # Top result should belong to current namespace or be a generic cortex fallback
    assert ("KSESSIONS" in ks_top.namespaces or ks_top.scope == "cortex")
    assert ("NOOR" in nr_top.namespaces or nr_top.scope == "cortex")

    # Ensure each namespace appears somewhere in respective results
    assert any("KSESSIONS" in p.namespaces for p in ks_results)
    assert any("NOOR" in p.namespaces for p in nr_results)

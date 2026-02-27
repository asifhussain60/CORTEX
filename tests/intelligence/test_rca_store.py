"""
Phase 87 — RCA Store Tests (RED phase — CORE-008)
Tests for RCAStore — SQLite persistence layer for RCA artefacts.

AC-PHASE87-003: RCAStore tests
CORE-008: TDD mandatory
CORE-011: Type hints
CORE-012: Docstrings
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def tmp_db_path(tmp_path: Path) -> Path:
    """Return a temp directory path for the RCA store database."""
    return tmp_path / "rca" / "rca_store.db"


@pytest.fixture
def rca_store(tmp_db_path: Path):
    """Return an RCAStore bound to a temporary database."""
    from cortex.intelligence.learning.rca_store import RCAStore
    store = RCAStore(db_path=str(tmp_db_path))
    store.initialize()
    return store


@pytest.fixture
def sample_rca():
    """Return a minimal RCAAnalysis suitable for persistence tests."""
    from cortex.intelligence.learning.rca_models import (
        RCAAnalysis, RCATemplate, RCACategory
    )
    return RCAAnalysis(
        id="RCA-STORE-001",
        failure_id="OPJ-store-001",
        methodology=RCATemplate.FIVE_WHYS,
        category=RCACategory.TECHNOLOGY,
        root_cause="Missing null guard on response handler",
        confidence=0.88,
    )


@pytest.fixture
def sample_rule():
    """Return a minimal PreventionRule suitable for persistence tests."""
    from cortex.intelligence.learning.rca_models import PreventionRule, GateLevel
    return PreventionRule(
        id="RULE-STORE-001",
        rca_id="RCA-STORE-001",
        rule_text="Enforce null check before accessing .response attribute",
        gate_level=GateLevel.ADVISORY,
    )


# ---------------------------------------------------------------------------
# Import
# ---------------------------------------------------------------------------
class TestRCAStoreImport:
    """Verify RCAStore can be imported and instantiated."""

    def test_rca_store_is_importable(self, tmp_db_path: Path) -> None:
        """RCAStore must be importable."""
        from cortex.intelligence.learning.rca_store import RCAStore
        assert RCAStore is not None

    def test_rca_store_is_instantiable(self, tmp_db_path: Path) -> None:
        """RCAStore must accept a db_path constructor argument."""
        from cortex.intelligence.learning.rca_store import RCAStore
        store = RCAStore(db_path=str(tmp_db_path))
        assert store is not None

    def test_rca_store_has_initialize(self, tmp_db_path: Path) -> None:
        """RCAStore must expose initialize() to set up the schema."""
        from cortex.intelligence.learning.rca_store import RCAStore
        assert hasattr(RCAStore, "initialize")

    def test_rca_store_has_save_analysis(self, tmp_db_path: Path) -> None:
        """RCAStore must expose save_analysis()."""
        from cortex.intelligence.learning.rca_store import RCAStore
        assert hasattr(RCAStore, "save_analysis")

    def test_rca_store_has_get_analysis(self, tmp_db_path: Path) -> None:
        """RCAStore must expose get_analysis()."""
        from cortex.intelligence.learning.rca_store import RCAStore
        assert hasattr(RCAStore, "get_analysis")

    def test_rca_store_has_save_rule(self, tmp_db_path: Path) -> None:
        """RCAStore must expose save_rule()."""
        from cortex.intelligence.learning.rca_store import RCAStore
        assert hasattr(RCAStore, "save_rule")

    def test_rca_store_has_list_rules(self, tmp_db_path: Path) -> None:
        """RCAStore must expose list_rules()."""
        from cortex.intelligence.learning.rca_store import RCAStore
        assert hasattr(RCAStore, "list_rules")


# ---------------------------------------------------------------------------
# initialize()
# ---------------------------------------------------------------------------
class TestRCAStoreInitialize:
    """Tests for RCAStore.initialize() — schema creation."""

    def test_initialize_creates_db_file(self, tmp_db_path: Path) -> None:
        """initialize() must create the SQLite database file."""
        from cortex.intelligence.learning.rca_store import RCAStore
        store = RCAStore(db_path=str(tmp_db_path))
        store.initialize()
        assert tmp_db_path.exists()

    def test_initialize_creates_parent_dirs(self, tmp_path: Path) -> None:
        """initialize() must create all parent directories."""
        deep_path = tmp_path / "a" / "b" / "c" / "rca_store.db"
        from cortex.intelligence.learning.rca_store import RCAStore
        store = RCAStore(db_path=str(deep_path))
        store.initialize()
        assert deep_path.exists()

    def test_initialize_is_idempotent(self, rca_store) -> None:
        """Calling initialize() twice must not raise an error."""
        rca_store.initialize()  # second call — must be safe


# ---------------------------------------------------------------------------
# save_analysis / get_analysis
# ---------------------------------------------------------------------------
class TestRCAStoreSaveGetAnalysis:
    """Tests for save_analysis() and get_analysis() round-trip."""

    def test_save_and_retrieve_analysis(self, rca_store, sample_rca) -> None:
        """An analysis saved with save_analysis() must be retrievable via get_analysis()."""
        rca_store.save_analysis(sample_rca)
        retrieved = rca_store.get_analysis(sample_rca.id)
        assert retrieved is not None
        assert retrieved.id == sample_rca.id

    def test_retrieved_analysis_has_correct_failure_id(self, rca_store, sample_rca) -> None:
        """Retrieved analysis must preserve failure_id."""
        rca_store.save_analysis(sample_rca)
        retrieved = rca_store.get_analysis(sample_rca.id)
        assert retrieved.failure_id == sample_rca.failure_id

    def test_retrieved_analysis_has_correct_methodology(self, rca_store, sample_rca) -> None:
        """Retrieved analysis must preserve methodology enum value."""
        rca_store.save_analysis(sample_rca)
        retrieved = rca_store.get_analysis(sample_rca.id)
        assert retrieved.methodology == sample_rca.methodology

    def test_get_analysis_returns_none_for_unknown_id(self, rca_store) -> None:
        """get_analysis() must return None when the id does not exist."""
        result = rca_store.get_analysis("NONEXISTENT-RCA-ID")
        assert result is None

    def test_list_analyses_returns_all_saved(self, rca_store, sample_rca) -> None:
        """list_analyses() must return all persisted analyses."""
        rca_store.save_analysis(sample_rca)
        results = rca_store.list_analyses()
        assert len(results) >= 1
        ids = [r.id for r in results]
        assert sample_rca.id in ids


# ---------------------------------------------------------------------------
# save_rule / list_rules
# ---------------------------------------------------------------------------
class TestRCAStoreSaveListRules:
    """Tests for save_rule() and list_rules()."""

    def test_save_and_list_rule(self, rca_store, sample_rule) -> None:
        """A rule saved with save_rule() must appear in list_rules()."""
        rca_store.save_rule(sample_rule)
        rules = rca_store.list_rules()
        assert any(r.id == sample_rule.id for r in rules)

    def test_saved_rule_preserves_gate_level(self, rca_store, sample_rule) -> None:
        """Saved rule must preserve gate_level enum value."""
        rca_store.save_rule(sample_rule)
        rules = rca_store.list_rules()
        matched = next(r for r in rules if r.id == sample_rule.id)
        assert matched.gate_level == sample_rule.gate_level

    def test_list_rules_empty_when_no_rules(self, rca_store) -> None:
        """list_rules() must return an empty list when no rules have been saved."""
        assert rca_store.list_rules() == []

    def test_list_rules_by_rca_id(self, rca_store, sample_rule) -> None:
        """list_rules(rca_id=...) must filter rules by rca_id."""
        rca_store.save_rule(sample_rule)
        rules = rca_store.list_rules(rca_id=sample_rule.rca_id)
        assert len(rules) >= 1
        assert all(r.rca_id == sample_rule.rca_id for r in rules)

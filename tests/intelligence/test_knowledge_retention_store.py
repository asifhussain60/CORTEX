"""
Phase 59-h (GAP-59-11): KnowledgeRetentionStore Tests
======================================================
Verifies that tier1_learned has a KnowledgeRetentionStore that provides
session-learning persistence — making the 'tier1_learned' name accurate.

TDD: RED → GREEN → REFACTOR (CORE-008)
"""
from __future__ import annotations

import time
from pathlib import Path

import pytest


class TestKnowledgeRetentionStoreImport:
    """KnowledgeRetentionStore is importable from canonical path (GAP-59-11)."""

    def test_imports_from_tier1_learned(self):
        from cortex.intelligence.memory.tier1_learned.knowledge_retention_store import (
            KnowledgeRetentionStore,
        )
        assert KnowledgeRetentionStore is not None

    def test_importable_from_tier1_learned_init(self):
        from cortex.intelligence.memory import tier1_learned
        assert hasattr(tier1_learned, "KnowledgeRetentionStore")

    def test_class_docstring_present(self):
        from cortex.intelligence.memory.tier1_learned.knowledge_retention_store import (
            KnowledgeRetentionStore,
        )
        assert KnowledgeRetentionStore.__doc__ is not None
        assert len(KnowledgeRetentionStore.__doc__.strip()) > 10


class TestKnowledgeRetentionStoreBasicAPI:
    """KnowledgeRetentionStore exposes session-learning persistence API."""

    @pytest.fixture
    def store(self):
        from cortex.intelligence.memory.tier1_learned.knowledge_retention_store import (
            KnowledgeRetentionStore,
        )
        return KnowledgeRetentionStore()

    def test_store_instantiates(self, store):
        assert store is not None

    def test_remember_stores_value(self, store):
        store.remember("test_key", "test_value")
        assert store.recall("test_key") == "test_value"

    def test_recall_unknown_key_returns_none(self, store):
        result = store.recall("nonexistent_key_xyz_abc")
        assert result is None

    def test_recall_unknown_key_returns_default(self, store):
        result = store.recall("nonexistent_key_xyz_abc", default="fallback")
        assert result == "fallback"

    def test_remember_overwrites_existing(self, store):
        store.remember("key", "value1")
        store.remember("key", "value2")
        assert store.recall("key") == "value2"

    def test_forget_removes_key(self, store):
        store.remember("forget_me", "gone")
        store.forget("forget_me")
        assert store.recall("forget_me") is None

    def test_forget_nonexistent_key_is_noop(self, store):
        # Must not raise
        store.forget("no_such_key_xyz")

    def test_list_keys_empty_on_new_store(self, store):
        keys = store.list_keys()
        assert isinstance(keys, list)

    def test_list_keys_after_remember(self, store):
        store.remember("alpha", 1)
        store.remember("beta", 2)
        keys = store.list_keys()
        assert "alpha" in keys
        assert "beta" in keys

    def test_remember_complex_value(self, store):
        payload = {"orchestrator": "MasterOrchestrator", "tdd_cycle": 3, "tags": ["p0", "p1"]}
        store.remember("session_state", payload)
        recalled = store.recall("session_state")
        assert recalled == payload

    def test_remember_accepts_domain_tag(self, store):
        """Optional domain tag for namespaced retention."""
        store.remember("key", "val", domain="tdd")
        # Should not raise; recall by key still works
        assert store.recall("key") == "val"

    def test_summarize_returns_dict(self, store):
        store.remember("x", 1)
        summary = store.summarize()
        assert isinstance(summary, dict)
        assert "total_entries" in summary


class TestKnowledgeRetentionStorePurposeAccuracy:
    """tier1_learned __init__.py documents dual purpose (cleaners + memory)."""

    def test_init_docstring_mentions_cleaners(self):
        import cortex.intelligence.memory.tier1_learned as m
        doc = m.__doc__ or ""
        assert "cleaner" in doc.lower() or "vacuum" in doc.lower(), (
            "tier1_learned docstring should mention cleaners"
        )

    def test_init_docstring_mentions_memory(self):
        import cortex.intelligence.memory.tier1_learned as m
        doc = m.__doc__ or ""
        assert "memory" in doc.lower() or "retention" in doc.lower(), (
            "tier1_learned docstring should mention memory/retention"
        )

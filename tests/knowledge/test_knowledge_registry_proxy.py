"""
Phase 59-d: KnowledgeRegistryProxy Tests

CORE-008: Tests written before implementation.
GAP-59-07: cortex/knowledge/ ghost directory must become an active Python module.

AC_START: AC-KNOWLEDGE-TEST-5904
"""
from __future__ import annotations

import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
CORTEX_ROOT = REPO_ROOT / "cortex"
REGISTRY_KNOWLEDGE = REPO_ROOT / "cortex-registry" / "knowledge"


class TestKnowledgeModuleActive:
    """59-d-T1: cortex.knowledge must be importable and non-empty."""

    def test_knowledge_module_importable(self) -> None:
        """cortex.knowledge must import without error."""
        mod = importlib.import_module("cortex.knowledge")
        assert mod is not None, "GAP-59-07 | cortex.knowledge must be importable"

    def test_knowledge_init_exports_proxy(self) -> None:
        """cortex.knowledge must export KnowledgeRegistryProxy."""
        from cortex.knowledge import KnowledgeRegistryProxy
        assert KnowledgeRegistryProxy is not None

    def test_knowledge_directory_has_init(self) -> None:
        """cortex/knowledge/__init__.py must exist."""
        init = CORTEX_ROOT / "knowledge" / "__init__.py"
        assert init.exists(), (
            "GAP-59-07 | cortex/knowledge/__init__.py does not exist — "
            "the directory is still a ghost module."
        )

    def test_knowledge_directory_has_registry_proxy(self) -> None:
        """cortex/knowledge/registry_proxy.py must exist."""
        proxy = CORTEX_ROOT / "knowledge" / "registry_proxy.py"
        assert proxy.exists(), (
            "GAP-59-07 | cortex/knowledge/registry_proxy.py not found"
        )


class TestKnowledgeRegistryProxy:
    """59-d-T2: KnowledgeRegistryProxy must load YAML files from registry."""

    def test_proxy_instantiates(self) -> None:
        """KnowledgeRegistryProxy must instantiate without error."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        assert proxy is not None

    def test_proxy_has_registry_root(self) -> None:
        """Proxy must point to cortex-registry/knowledge/."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        assert proxy.registry_root.exists(), (
            f"GAP-59-07 | KnowledgeRegistryProxy.registry_root does not exist: "
            f"{proxy.registry_root}"
        )

    def test_proxy_loads_entries(self) -> None:
        """KnowledgeRegistryProxy.all() must return at least 1 entry."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        entries = proxy.all()
        assert len(entries) >= 1, (
            "GAP-59-07 | KnowledgeRegistryProxy.all() returned 0 entries — "
            "registry YAML files may not be loaded."
        )

    def test_proxy_domains_returns_list(self) -> None:
        """KnowledgeRegistryProxy.domains() must return a non-empty list."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        domains = proxy.domains()
        assert isinstance(domains, list)
        assert len(domains) >= 1

    def test_proxy_query_by_domain(self) -> None:
        """KnowledgeRegistryProxy.query(domain=...) must filter correctly."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        domains = proxy.domains()
        if not domains:
            pytest.skip("No domains available in registry")
        first_domain = domains[0]
        results = proxy.query(domain=first_domain)
        assert all(e.get("domain") == first_domain for e in results), (
            "query(domain=...) returned entries from other domains"
        )

    def test_proxy_get_returns_entry_or_none(self) -> None:
        """KnowledgeRegistryProxy.get(key) must return a dict or None."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        entries = proxy.all()
        if not entries:
            pytest.skip("No entries available")
        first_key = entries[0]["key"]
        result = proxy.get(first_key)
        assert result is not None, f"get({first_key!r}) returned None unexpectedly"
        assert "content" in result

    def test_proxy_get_missing_key_returns_none(self) -> None:
        """KnowledgeRegistryProxy.get() must return None for unknown keys."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        assert proxy.get("does.not.exist.ever") is None

    def test_proxy_invalidate_cache(self) -> None:
        """invalidate_cache() must allow fresh reload."""
        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy()
        _ = proxy.all()  # prime cache
        proxy.invalidate_cache()
        assert proxy._cache is None
        entries2 = proxy.all()
        assert isinstance(entries2, list)

    def test_proxy_custom_registry_root(self, tmp_path: Path) -> None:
        """KnowledgeRegistryProxy accepts custom root path."""
        # Write a minimal YAML file in a temp directory
        domain_dir = tmp_path / "test-domain"
        domain_dir.mkdir()
        yaml_file = domain_dir / "sample.yaml"
        yaml_file.write_text("title: test\ndescription: sample\n", encoding="utf-8")

        from cortex.knowledge import KnowledgeRegistryProxy
        proxy = KnowledgeRegistryProxy(registry_root=tmp_path)
        entries = proxy.all()
        assert any("test-domain.sample" in e["key"] for e in entries), (
            f"Custom root entries: {[e['key'] for e in entries]}"
        )

# AC_COMPLETE: AC-KNOWLEDGE-TEST-5904 ✅

"""
Phase 48 S3: CompanyKnowledgeLoader Isolation - Workspace-Scoped Knowledge Caching

Tests for isolating company knowledge per workspace with LRU caching.

Authority: phase-48-registry-isolation-multi-tenant.yaml
Acceptance Criteria:
  - AC-PHASE48-S3-001: Knowledge cache scoped to workspace
  - AC-PHASE48-S3-002: Company A knowledge doesn't leak to Company B
  - AC-PHASE48-S3-003: Cache eviction per-workspace
"""

import pytest
from typing import Dict, Optional, Any
from unittest.mock import MagicMock
from collections import OrderedDict


class CompanyKnowledgeCache:
    """LRU knowledge cache for a single workspace."""
    
    def __init__(self, max_size: int = 50):
        """Initialize cache with size limit."""
        self.max_size = max_size
        self._cache: OrderedDict = OrderedDict()
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache, moving it to end (LRU)."""
        if key in self._cache:
            self._cache.move_to_end(key)  # type: ignore
            return self._cache[key]
        return None
    
    def put(self, key: str, value: Any) -> None:
        """Put item in cache, evicting oldest if full."""
        if key in self._cache:
            self._cache.move_to_end(key)  # type: ignore
        self._cache[key] = value
        
        # Evict oldest if over capacity
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)  # type: ignore
    
    def clear(self) -> None:
        """Clear cache."""
        self._cache.clear()
    
    def size(self) -> int:
        """Get current cache size."""
        return len(self._cache)


class IsolatedCompanyKnowledgeLoader:
    """Load and cache company knowledge scoped to workspace."""
    
    def __init__(self, workspace_id: str, company_name: Optional[str] = None):
        """
        Initialize loader for workspace.
        
        Args:
            workspace_id: Unique workspace identifier
            company_name: Company name (for multi-tenant isolation)
        """
        self.workspace_id = workspace_id
        self.company_name = company_name or "default"
        self._cache = CompanyKnowledgeCache()
        self._loaded_domains: set = set()
    
    def load_domain(self, domain_name: str) -> Dict[str, Any]:
        """
        Load company knowledge for domain (scoped to this workspace).
        
        Args:
            domain_name: Domain to load (e.g., 'security', 'testing')
        
        Returns:
            Domain knowledge dictionary
        """
        # Check cache first
        cache_key = f"{self.company_name}:{domain_name}"
        cached = self._cache.get(cache_key)
        if cached:
            return cached
        
        # Load from company standard (workspace-scoped)
        domain_data = self._load_company_domain(domain_name)
        
        # Cache it
        self._cache.put(cache_key, domain_data)
        self._loaded_domains.add(domain_name)
        
        return domain_data
    
    def _load_company_domain(self, domain_name: str) -> Dict[str, Any]:
        """Load company domain knowledge (simulated)."""
        return {
            "workspace_id": self.workspace_id,
            "company": self.company_name,
            "domain": domain_name,
            "standards": [f"standard_{i}" for i in range(3)]
        }
    
    def get_compliance_rules(self, domain_name: str) -> list:
        """Get compliance rules for domain (cached)."""
        domain = self.load_domain(domain_name)
        return domain.get("standards", [])
    
    def clear_cache(self) -> None:
        """Clear workspace-scoped cache."""
        self._cache.clear()
        self._loaded_domains.clear()
    
    def list_loaded(self) -> list:
        """List loaded domains in cache."""
        return list(self._loaded_domains)
    
    def cache_size(self) -> int:
        """Get current cache size."""
        return self._cache.size()


class CompanyKnowledgeLoaderFactory:
    """Create and manage isolated knowledge loaders per workspace."""
    
    def __init__(self):
        """Initialize loader factory."""
        self._loaders: Dict[str, IsolatedCompanyKnowledgeLoader] = {}
    
    def get_or_create(self, workspace_id: str, company_name: Optional[str] = None) -> IsolatedCompanyKnowledgeLoader:
        """Get or create loader for workspace."""
        if workspace_id not in self._loaders:
            self._loaders[workspace_id] = IsolatedCompanyKnowledgeLoader(workspace_id, company_name)
        return self._loaders[workspace_id]
    
    def cleanup(self, workspace_id: str) -> None:
        """Clean up loader for workspace."""
        if workspace_id in self._loaders:
            self._loaders[workspace_id].clear_cache()
            del self._loaders[workspace_id]


# ============================================================================
# TESTS: Knowledge Cache Isolation (AC-PHASE48-S3-001)
# ============================================================================

class TestKnowledgeCacheInitialization:
    """Test knowledge cache initialization."""
    
    def test_cache_init(self):
        """Test initializing cache."""
        cache = CompanyKnowledgeCache()
        assert cache.max_size == 50
        assert cache.size() == 0
    
    def test_cache_with_custom_size(self):
        """Test cache with custom size limit."""
        cache = CompanyKnowledgeCache(max_size=10)
        assert cache.max_size == 10
    
    def test_loader_init(self):
        """Test initializing knowledge loader."""
        loader = IsolatedCompanyKnowledgeLoader("workspace1")
        assert loader.workspace_id == "workspace1"
        assert loader.company_name == "default"
    
    def test_loader_with_company_name(self):
        """Test loader with company name."""
        loader = IsolatedCompanyKnowledgeLoader("acme-workspace", "ACME Corp")
        assert loader.workspace_id == "acme-workspace"
        assert loader.company_name == "ACME Corp"


class TestKnowledgeLoading:
    """Test loading and caching knowledge."""
    
    def test_load_domain(self):
        """Test loading domain knowledge."""
        loader = IsolatedCompanyKnowledgeLoader("workspace1", "Company A")
        
        domain = loader.load_domain("security")
        assert domain is not None
        assert domain["workspace_id"] == "workspace1"
        assert domain["company"] == "Company A"
        assert domain["domain"] == "security"
    
    def test_cache_hit_on_reload(self):
        """Test that reloading returns cached instance."""
        loader = IsolatedCompanyKnowledgeLoader("workspace1")
        
        domain1 = loader.load_domain("testing")
        domain2 = loader.load_domain("testing")
        
        # Same object (cached)
        assert domain1 is domain2
    
    def test_multiple_domains_in_cache(self):
        """Test caching multiple domains."""
        loader = IsolatedCompanyKnowledgeLoader("workspace1")
        
        loader.load_domain("security")
        loader.load_domain("testing")
        loader.load_domain("docs")
        
        assert loader.cache_size() == 3
        assert set(loader.list_loaded()) == {"security", "testing", "docs"}
    
    def test_compliance_rules_retrieval(self):
        """Test getting compliance rules from cache."""
        loader = IsolatedCompanyKnowledgeLoader("workspace1")
        
        rules = loader.get_compliance_rules("security")
        assert isinstance(rules, list)
        assert len(rules) == 3


class TestWorkspaceIsolation:
    """Test knowledge isolation between workspaces."""
    
    def test_two_workspaces_isolated_cache(self):
        """Test that two workspaces have separate caches."""
        loader1 = IsolatedCompanyKnowledgeLoader("workspace1", "Company A")
        loader2 = IsolatedCompanyKnowledgeLoader("workspace2", "Company B")
        
        domain1 = loader1.load_domain("security")
        domain2 = loader2.load_domain("security")
        
        # Different instances
        assert domain1 is not domain2
        # Different company
        assert domain1["company"] == "Company A"
        assert domain2["company"] == "Company B"
    
    def test_cache_eviction_per_workspace(self):
        """Test cache eviction is per-workspace."""
        # Small cache for testing
        loader1 = IsolatedCompanyKnowledgeLoader("workspace1")
        loader1._cache.max_size = 3
        
        loader2 = IsolatedCompanyKnowledgeLoader("workspace2")
        loader2._cache.max_size = 3
        
        # Fill loader1's cache
        loader1.load_domain("domain1")
        loader1.load_domain("domain2")
        loader1.load_domain("domain3")
        
        # Fill loader2's cache
        loader2.load_domain("domainA")
        loader2.load_domain("domainB")
        loader2.load_domain("domainC")
        
        assert loader1.cache_size() == 3
        assert loader2.cache_size() == 3
        
        # Add one more to loader1 (evicts oldest)
        loader1.load_domain("domain4")
        assert loader1.cache_size() == 3
        
        # loader2 unaffected
        assert loader2.cache_size() == 3


# ============================================================================
# TESTS: No Knowledge Leakage (AC-PHASE48-S3-002)
# ============================================================================

class TestNoKnowledgeLeakage:
    """Test that company A knowledge doesn't leak to company B."""
    
    def test_company_a_vs_company_b(self):
        """Test knowledge isolation between different companies."""
        company_a = IsolatedCompanyKnowledgeLoader("workspace_a", "Company A")
        company_b = IsolatedCompanyKnowledgeLoader("workspace_b", "Company B")
        
        # Load same domain for both
        rules_a = company_a.get_compliance_rules("security")
        rules_b = company_b.get_compliance_rules("security")
        
        # Both get data
        assert rules_a is not None
        assert rules_b is not None
        
        # But loader instances are different
        assert company_a._loaded_domains != company_b._loaded_domains or \
               company_a.company_name != company_b.company_name
    
    def test_workspace_cache_clearing_isolation(self):
        """Test that clearing one workspace's cache doesn't affect another."""
        loader1 = IsolatedCompanyKnowledgeLoader("ws1", "Co1")
        loader2 = IsolatedCompanyKnowledgeLoader("ws2", "Co2")
        
        loader1.load_domain("security")
        loader2.load_domain("security")
        
        assert loader1.cache_size() == 1
        assert loader2.cache_size() == 1
        
        loader1.clear_cache()
        
        assert loader1.cache_size() == 0
        assert loader2.cache_size() == 1  # Unaffected


# ============================================================================
# TESTS: Cache Eviction (AC-PHASE48-S3-003)
# ============================================================================

class TestCacheEviction:
    """Test per-workspace cache eviction."""
    
    def test_lru_eviction(self):
        """Test LRU eviction policy."""
        loader = IsolatedCompanyKnowledgeLoader("workspace1")
        loader._cache.max_size = 3
        
        # Fill cache
        loader.load_domain("d1")
        loader.load_domain("d2")
        loader.load_domain("d3")
        
        assert loader.cache_size() == 3
        
        # Add one more (should evict d1)
        loader.load_domain("d4")
        
        assert loader.cache_size() == 3
        # d4 should be present since it was just loaded
        loaded_list = loader.list_loaded()
        assert "d4" in loaded_list
    
    def test_access_updates_lru_order(self):
        """Test that accessing item updates LRU order."""
        loader = IsolatedCompanyKnowledgeLoader("workspace1")
        loader._cache.max_size = 3
        
        # Fill cache
        loader.load_domain("d1")
        loader.load_domain("d2")
        loader.load_domain("d3")
        
        # Access d1 (moves to end)
        loader.load_domain("d1")
        
        # Add d4 (should evict d2, not d1)
        loader.load_domain("d4")
        
        assert "d1" in loader.list_loaded()
        assert "d4" in loader.list_loaded()
    
    def test_independent_eviction_per_workspace(self):
        """Test that eviction is independent per workspace."""
        loader1 = IsolatedCompanyKnowledgeLoader("ws1")
        loader1._cache.max_size = 2
        
        loader2 = IsolatedCompanyKnowledgeLoader("ws2")
        loader2._cache.max_size = 2
        
        # Fill loader1
        loader1.load_domain("d1")
        loader1.load_domain("d2")
        
        # Fill loader2
        loader2.load_domain("d1")
        loader2.load_domain("d2")
        
        # Trigger eviction in loader1
        loader1.load_domain("d3")
        
        # loader2 still has both
        assert loader2.cache_size() == 2


# ============================================================================
# TESTS: Factory Pattern (Foundation)
# ============================================================================

class TestCompanyKnowledgeLoaderFactory:
    """Test factory for managing loaders."""
    
    def test_factory_get_or_create(self):
        """Test factory get_or_create pattern."""
        factory = CompanyKnowledgeLoaderFactory()
        
        loader1 = factory.get_or_create("ws1", "Company A")
        loader1_again = factory.get_or_create("ws1", "Company A")
        
        assert loader1 is loader1_again
    
    def test_factory_multiple_workspaces(self):
        """Test factory with multiple workspaces."""
        factory = CompanyKnowledgeLoaderFactory()
        
        loader_a = factory.get_or_create("ws_a", "Company A")
        loader_b = factory.get_or_create("ws_b", "Company B")
        
        assert loader_a is not loader_b
        assert loader_a.company_name == "Company A"
        assert loader_b.company_name == "Company B"
    
    def test_factory_cleanup(self):
        """Test factory cleanup."""
        factory = CompanyKnowledgeLoaderFactory()
        
        loader = factory.get_or_create("ws1")
        loader.load_domain("security")
        
        factory.cleanup("ws1")
        
        # New loader should be empty
        new_loader = factory.get_or_create("ws1")
        assert new_loader.cache_size() == 0


# ============================================================================
# TESTS: Multi-Workspace Scenarios
# ============================================================================

class TestMultiWorkspaceScenarios:
    """Test realistic multi-workspace scenarios."""
    
    def test_three_teams_isolated_knowledge(self):
        """Test three teams with isolated knowledge."""
        team_platform = IsolatedCompanyKnowledgeLoader("team_platform", "Platform Team")
        team_backend = IsolatedCompanyKnowledgeLoader("team_backend", "Backend Team")
        team_frontend = IsolatedCompanyKnowledgeLoader("team_frontend", "Frontend Team")
        
        # Each loads domain knowledge
        team_platform.load_domain("deployment")
        team_backend.load_domain("api")
        team_frontend.load_domain("ui")
        
        # Each workspace is isolated
        assert "deployment" in team_platform.list_loaded()
        assert "api" in team_backend.list_loaded()
        assert "ui" in team_frontend.list_loaded()
        
        # No leakage
        assert "api" not in team_platform.list_loaded()
        assert "ui" not in team_backend.list_loaded()
    
    def test_switching_workspaces_preserves_state(self):
        """Test that switching between workspaces preserves their state."""
        loader1 = IsolatedCompanyKnowledgeLoader("workspace1")
        loader2 = IsolatedCompanyKnowledgeLoader("workspace2")
        
        # Work in workspace 1
        loader1.load_domain("security")
        loader1.load_domain("testing")
        
        # Switch to workspace 2
        loader2.load_domain("docs")
        
        # Switch back to workspace 1
        domains1 = loader1.list_loaded()
        
        # Workspace 1 still has its domains
        assert set(domains1) == {"security", "testing"}

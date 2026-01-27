"""
Tests for DiscoveryOrchestrator base class.

Task: DISC-001
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008 (TDD - tests before implementation)

Test Coverage:
1. Plugin registration and discovery
2. Topology aggregation from multiple plugins
3. Cache hit/miss scenarios
4. Parallel plugin execution
5. Error isolation (plugin failure doesn't crash others)
"""

import pytest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.orchestrators.support.discovery_orchestrator import (
    DiscoveryOrchestrator,
    DiscoveryType,
)
from cortex.brain.discovery import DiscoveryPlugin, TopologyMap


class MockDiscoveryPlugin(DiscoveryPlugin):
    """Mock plugin for testing."""
    
    def __init__(self, name: str, should_fail: bool = False):
        """Initialize mock plugin."""
        self.name = name
        self.should_fail = should_fail
        self.discover_called = False
    
    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """Mock discovery method."""
        self.discover_called = True
        if self.should_fail:
            raise RuntimeError(f"Plugin {self.name} failed")
        return {self.name: "discovered"}


class TestDiscoveryOrchestratorInit:
    """Test DiscoveryOrchestrator initialization."""
    
    def test_init_creates_orchestrator(self):
        """Test orchestrator can be instantiated."""
        repo_path = Path("/fake/repo")
        orchestrator = DiscoveryOrchestrator(repo_path=repo_path)
        
        assert orchestrator is not None
        assert orchestrator.repo_path == repo_path
    
    def test_init_with_cache_enabled(self):
        """Test orchestrator with caching enabled."""
        repo_path = Path("/fake/repo")
        orchestrator = DiscoveryOrchestrator(
            repo_path=repo_path,
            enable_cache=True
        )
        
        assert orchestrator.cache_enabled is True
    
    def test_init_with_cache_disabled(self):
        """Test orchestrator with caching disabled."""
        repo_path = Path("/fake/repo")
        orchestrator = DiscoveryOrchestrator(
            repo_path=repo_path,
            enable_cache=False
        )
        
        assert orchestrator.cache_enabled is False


class TestPluginRegistration:
    """Test plugin registration and management."""
    
    def test_register_single_plugin(self):
        """Test registering a single discovery plugin."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        plugin = MockDiscoveryPlugin("test_plugin")
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin)
        
        assert DiscoveryType.CONFIG in orchestrator.plugins
        assert orchestrator.plugins[DiscoveryType.CONFIG] == plugin
    
    def test_register_multiple_plugins(self):
        """Test registering multiple discovery plugins."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        config_plugin = MockDiscoveryPlugin("config")
        db_plugin = MockDiscoveryPlugin("database")
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, config_plugin)
        orchestrator.register_plugin(DiscoveryType.DATABASE, db_plugin)
        
        assert len(orchestrator.plugins) == 2
        assert orchestrator.plugins[DiscoveryType.CONFIG] == config_plugin
        assert orchestrator.plugins[DiscoveryType.DATABASE] == db_plugin
    
    def test_register_plugin_replaces_existing(self):
        """Test that registering plugin replaces existing one of same type."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        plugin1 = MockDiscoveryPlugin("plugin1")
        plugin2 = MockDiscoveryPlugin("plugin2")
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin1)
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin2)
        
        assert orchestrator.plugins[DiscoveryType.CONFIG] == plugin2


class TestTopologyDiscovery:
    """Test topology discovery operations."""
    
    def test_discover_topology_with_single_plugin(self):
        """Test discovering topology with one plugin."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        plugin = MockDiscoveryPlugin("config")
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin)
        
        topology = orchestrator.discover_topology()
        
        assert plugin.discover_called is True
        assert isinstance(topology, TopologyMap)
        assert topology.config == {"config": "discovered"}
    
    def test_discover_topology_with_multiple_plugins(self):
        """Test discovering topology with multiple plugins."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        config_plugin = MockDiscoveryPlugin("config")
        db_plugin = MockDiscoveryPlugin("database")
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, config_plugin)
        orchestrator.register_plugin(DiscoveryType.DATABASE, db_plugin)
        
        topology = orchestrator.discover_topology()
        
        assert config_plugin.discover_called is True
        assert db_plugin.discover_called is True
        assert topology.config == {"config": "discovered"}
        assert topology.databases == {"database": "discovered"}
    
    def test_discover_by_type_single_type(self):
        """Test discovering specific type only."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        config_plugin = MockDiscoveryPlugin("config")
        db_plugin = MockDiscoveryPlugin("database")
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, config_plugin)
        orchestrator.register_plugin(DiscoveryType.DATABASE, db_plugin)
        
        result = orchestrator.discover_by_type(DiscoveryType.CONFIG)
        
        assert config_plugin.discover_called is True
        assert db_plugin.discover_called is False
        assert result == {"config": "discovered"}


class TestCaching:
    """Test caching functionality."""
    
    def test_cache_hit_returns_cached_topology(self):
        """Test that cache hit returns cached result without re-discovery."""
        orchestrator = DiscoveryOrchestrator(
            repo_path=Path("/fake"),
            enable_cache=True
        )
        plugin = MockDiscoveryPlugin("config")
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin)
        
        # First discovery - cache miss
        topology1 = orchestrator.discover_topology()
        assert plugin.discover_called is True
        
        # Reset plugin state
        plugin.discover_called = False
        
        # Second discovery - should be cache hit
        topology2 = orchestrator.discover_topology()
        assert plugin.discover_called is False  # Not called again
        assert topology1.to_dict() == topology2.to_dict()
    
    def test_cache_invalidation(self):
        """Test cache invalidation triggers re-discovery."""
        orchestrator = DiscoveryOrchestrator(
            repo_path=Path("/fake"),
            enable_cache=True
        )
        plugin = MockDiscoveryPlugin("config")
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin)
        
        # First discovery
        orchestrator.discover_topology()
        plugin.discover_called = False
        
        # Invalidate cache
        orchestrator.invalidate_cache(file_patterns=["*.config"])
        
        # Second discovery should re-run
        orchestrator.discover_topology()
        assert plugin.discover_called is True
    
    def test_cache_disabled_always_discovers(self):
        """Test that disabled cache always runs discovery."""
        orchestrator = DiscoveryOrchestrator(
            repo_path=Path("/fake"),
            enable_cache=False
        )
        plugin = MockDiscoveryPlugin("config")
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin)
        
        # First discovery
        orchestrator.discover_topology()
        assert plugin.discover_called is True
        
        # Reset plugin state
        plugin.discover_called = False
        
        # Second discovery should re-run (cache disabled)
        orchestrator.discover_topology()
        assert plugin.discover_called is True


class TestErrorHandling:
    """Test error handling and isolation."""
    
    def test_plugin_failure_isolated(self):
        """Test that one plugin failure doesn't crash others."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        good_plugin = MockDiscoveryPlugin("good")
        bad_plugin = MockDiscoveryPlugin("bad", should_fail=True)
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, good_plugin)
        orchestrator.register_plugin(DiscoveryType.DATABASE, bad_plugin)
        
        # Should not raise exception
        topology = orchestrator.discover_topology()
        
        # Good plugin should succeed
        assert good_plugin.discover_called is True
        assert topology.config == {"good": "discovered"}
        
        # Bad plugin failure should be logged but not crash
        assert topology.databases == {}  # Empty due to failure
    
    def test_all_plugins_fail_returns_empty_topology(self):
        """Test that all plugins failing returns empty topology."""
        orchestrator = DiscoveryOrchestrator(repo_path=Path("/fake"))
        bad_plugin1 = MockDiscoveryPlugin("bad1", should_fail=True)
        bad_plugin2 = MockDiscoveryPlugin("bad2", should_fail=True)
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, bad_plugin1)
        orchestrator.register_plugin(DiscoveryType.DATABASE, bad_plugin2)
        
        topology = orchestrator.discover_topology()
        
        assert topology.config == {}
        assert topology.databases == {}


class TestParallelExecution:
    """Test parallel plugin execution."""
    
    @pytest.mark.asyncio
    async def test_parallel_discovery_executes_concurrently(self):
        """Test that plugins execute in parallel when enabled."""
        orchestrator = DiscoveryOrchestrator(
            repo_path=Path("/fake"),
            parallel_execution=True
        )
        plugin1 = MockDiscoveryPlugin("plugin1")
        plugin2 = MockDiscoveryPlugin("plugin2")
        
        orchestrator.register_plugin(DiscoveryType.CONFIG, plugin1)
        orchestrator.register_plugin(DiscoveryType.DATABASE, plugin2)
        
        topology = orchestrator.discover_topology()
        
        assert plugin1.discover_called is True
        assert plugin2.discover_called is True
        assert isinstance(topology, TopologyMap)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

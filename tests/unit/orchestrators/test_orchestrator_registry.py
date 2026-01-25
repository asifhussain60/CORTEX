"""
Orchestrator Registry Tests - AR-017-01 (AC-PERMANENT-FIX-012)

Tests for orchestrator registration and discovery system.
- Registry bridges to DatabaseBackedRegistry
- Discovery API returns orchestrators by domain/capability  
- Registration validates required interfaces

Author: Asif Hussain
"""

import pytest

# AC-PERMANENT-FIX-012: Use DatabaseBackedRegistry bridge
from cortex.orchestrators.registry import (
    OrchestratorRegistry,
    OrchestratorMetadata,
)
from cortex.orchestrators.registry.discovery_engine import (
    DiscoveryEngine,
    DiscoveryQuery,
    DiscoveryResult,
)
from cortex.orchestrators import get_database_registry


class TestOrchestratorRegistryBridge:
    """Test orchestrator registry bridge to DatabaseBackedRegistry"""
    
    def test_registry_singleton(self):
        """Test that registry bridge works"""
        # AC-PERMANENT-FIX-012: Bridge to DatabaseBackedRegistry
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - registry1 = OrchestratorRegistry()
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - registry2 = OrchestratorRegistry()
        
        assert registry1 is registry2
    
    def test_register_orchestrator(self):
        """Test registering an orchestrator (bridge compatibility)"""
        # AC-PERMANENT-FIX-012: Bridge to DatabaseBackedRegistry 
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - registry = OrchestratorRegistry()
        registry.clear()  # Clear for clean test (no-op in bridge)
        
        metadata = OrchestratorMetadata(
            name="test-orchestrator",
            class_type=None,  # Bridge compatibility
        )
        
        # Bridge registration is no-op, but should not fail
        registry.register(
            orchestrator_id="test-orch-1",
            orchestrator_name="Test Orchestrator", 
            orchestrator_class=type,
            tier_dependencies={0, 1},
            description="Test orchestrator",
        )
        
        assert registry.get("test-orch-1") is not None
    
    def test_register_validates_required_fields(self):
        """Test that registration validates required fields (bridge compatibility)"""
        # AC-PERMANENT-FIX-012: Use bridge to DatabaseBackedRegistry
# REMOVED: Manual registry pattern - # REMOVED: Manual registry pattern - registry = OrchestratorRegistry()
        registry.clear()
        
        # Missing domain field - should raise error
        with pytest.raises((ValueError, TypeError)):
            metadata = OrchestratorMetadata(
                id="test-orch",
                name="Test",
                domain="",  # Empty domain
                version="1.0",
                capabilities=[],
                description="Test",
            )
    
    def test_get_orchestrator_by_id(self):
        """Test getting orchestrator by ID"""
        registry = get_database_registry()
        registry.clear()
        
        metadata = OrchestratorMetadata(
            id="test-1",
            name="Test",
            domain="planning",
            version="1.0",
            capabilities=[],
            description="Test",
        )
        registry.register(metadata)
        
        retrieved = registry.get("test-1")
        assert retrieved is not None
        assert retrieved.id == "test-1"
    
    def test_get_nonexistent_orchestrator(self):
        """Test getting nonexistent orchestrator returns None"""
        registry = get_database_registry()
        retrieved = registry.get("nonexistent")
        assert retrieved is None
    
    def test_list_all_orchestrators(self):
        """Test listing all registered orchestrators"""
        registry = get_database_registry()
        registry.clear()
        
        # Register multiple
        for i in range(3):
            metadata = OrchestratorMetadata(
                id=f"test-{i}",
                name=f"Test {i}",
                domain="planning",
                version="1.0",
                capabilities=[],
                description=f"Test {i}",
            )
            registry.register(metadata)
        
        all_orchs = registry.list_all()
        assert len(all_orchs) == 3
    
    def test_unregister_orchestrator(self):
        """Test unregistering an orchestrator"""
        registry = get_database_registry()
        registry.clear()
        
        metadata = OrchestratorMetadata(
            id="test-1",
            name="Test",
            domain="planning",
            version="1.0",
            capabilities=[],
            description="Test",
        )
        registry.register(metadata)
        assert registry.get("test-1") is not None
        
        registry.unregister("test-1")
        assert registry.get("test-1") is None
    
    def test_registry_statistics(self):
        """Test getting registry statistics"""
        registry = get_database_registry()
        registry.clear()
        
        for i in range(5):
            metadata = OrchestratorMetadata(
                id=f"test-{i}",
                name=f"Test {i}",
                domain="planning" if i % 2 == 0 else "execution",
                version="1.0",
                capabilities=["cap1", "cap2"] if i % 2 == 0 else ["cap3"],
                description=f"Test {i}",
            )
            registry.register(metadata)
        
        stats = registry.get_statistics()
        assert stats["total_orchestrators"] == 5
        assert stats["total_domains"] == 2
        assert stats["total_capabilities"] >= 3


class TestDiscoveryEngine:
    """Test orchestrator discovery engine"""
    
    def test_discovery_singleton(self):
        """Test that discovery engine is singleton"""
        engine1 = DiscoveryEngine()
        engine2 = DiscoveryEngine()
        
        assert engine1 is engine2
    
    def test_query_by_domain(self):
        """Test querying orchestrators by domain"""
        registry = get_database_registry()
        registry.clear()
        
        # Register orchestrators
        for i in range(3):
            metadata = OrchestratorMetadata(
                id=f"planning-{i}",
                name=f"Planning {i}",
                domain="planning",
                version="1.0",
                capabilities=["plan"],
                description=f"Planning {i}",
            )
            registry.register(metadata)
        
        for i in range(2):
            metadata = OrchestratorMetadata(
                id=f"execution-{i}",
                name=f"Execution {i}",
                domain="execution",
                version="1.0",
                capabilities=["execute"],
                description=f"Execution {i}",
            )
            registry.register(metadata)
        
        engine = DiscoveryEngine()
        query = DiscoveryQuery(domain="planning")
        results = engine.search(query)
        
        assert len(results.orchestrators) == 3
        assert all(o.domain == "planning" for o in results.orchestrators)
    
    def test_query_by_capability(self):
        """Test querying orchestrators by capability"""
        registry = get_database_registry()
        registry.clear()
        
        # Register orchestrators with different capabilities
        metadata1 = OrchestratorMetadata(
            id="test-1",
            name="Test 1",
            domain="planning",
            version="1.0",
            capabilities=["analyze", "execute"],
            description="Test 1",
        )
        registry.register(metadata1)
        
        metadata2 = OrchestratorMetadata(
            id="test-2",
            name="Test 2",
            domain="execution",
            version="1.0",
            capabilities=["execute"],
            description="Test 2",
        )
        registry.register(metadata2)
        
        metadata3 = OrchestratorMetadata(
            id="test-3",
            name="Test 3",
            domain="analysis",
            version="1.0",
            capabilities=["analyze"],
            description="Test 3",
        )
        registry.register(metadata3)
        
        engine = DiscoveryEngine()
        query = DiscoveryQuery(capability="execute")
        results = engine.search(query)
        
        assert len(results.orchestrators) == 2
        assert all("execute" in o.capabilities for o in results.orchestrators)
    
    def test_query_by_domain_and_capability(self):
        """Test querying by both domain and capability"""
        registry = get_database_registry()
        registry.clear()
        
        # Register varied orchestrators
        metadata1 = OrchestratorMetadata(
            id="planning-1",
            name="Planning 1",
            domain="planning",
            version="1.0",
            capabilities=["plan", "analyze"],
            description="Planning 1",
        )
        registry.register(metadata1)
        
        metadata2 = OrchestratorMetadata(
            id="planning-2",
            name="Planning 2",
            domain="planning",
            version="1.0",
            capabilities=["plan"],
            description="Planning 2",
        )
        registry.register(metadata2)
        
        metadata3 = OrchestratorMetadata(
            id="analysis-1",
            name="Analysis 1",
            domain="analysis",
            version="1.0",
            capabilities=["analyze"],
            description="Analysis 1",
        )
        registry.register(metadata3)
        
        engine = DiscoveryEngine()
        query = DiscoveryQuery(domain="planning", capability="analyze")
        results = engine.search(query)
        
        assert len(results.orchestrators) == 1
        assert results.orchestrators[0].id == "planning-1"
    
    def test_query_by_version(self):
        """Test querying by version"""
        registry = get_database_registry()
        registry.clear()
        
        for version in ["1.0", "2.0"]:
            metadata = OrchestratorMetadata(
                id=f"test-v{version.replace('.', '-')}",
                name=f"Test {version}",
                domain="planning",
                version=version,
                capabilities=[],
                description=f"Test {version}",
            )
            registry.register(metadata)
        
        # Register another with 1.0
        metadata = OrchestratorMetadata(
            id="test-v1-second",
            name="Test 1.0 Second",
            domain="planning",
            version="1.0",
            capabilities=[],
            description="Test 1.0 Second",
        )
        registry.register(metadata)
        
        engine = DiscoveryEngine()
        query = DiscoveryQuery(version="1.0")
        results = engine.search(query)
        
        assert len(results.orchestrators) == 2
        assert all(o.version == "1.0" for o in results.orchestrators)
    
    def test_query_returns_empty_when_no_matches(self):
        """Test query returns empty results when no matches"""
        registry = get_database_registry()
        registry.clear()
        
        metadata = OrchestratorMetadata(
            id="test-1",
            name="Test",
            domain="planning",
            version="1.0",
            capabilities=["plan"],
            description="Test",
        )
        registry.register(metadata)
        
        engine = DiscoveryEngine()
        query = DiscoveryQuery(domain="nonexistent")
        results = engine.search(query)
        
        assert len(results.orchestrators) == 0
        assert results.total_found == 0


class TestDiscoveryResult:
    """Test discovery result format"""
    
    def test_result_contains_orchestrators(self):
        """Test that result contains orchestrators"""
        registry = get_database_registry()
        registry.clear()
        
        metadata = OrchestratorMetadata(
            id="test-1",
            name="Test",
            domain="planning",
            version="1.0",
            capabilities=["test"],
            description="Test",
        )
        registry.register(metadata)
        
        engine = DiscoveryEngine()
        query = DiscoveryQuery(domain="planning")
        results = engine.search(query)
        
        assert hasattr(results, "orchestrators")
        assert len(results.orchestrators) > 0
    
    def test_result_contains_metadata(self):
        """Test that result contains search metadata"""
        registry = get_database_registry()
        registry.clear()
        
        for i in range(5):
            metadata = OrchestratorMetadata(
                id=f"test-{i}",
                name=f"Test {i}",
                domain="planning",
                version="1.0",
                capabilities=[],
                description=f"Test {i}",
            )
            registry.register(metadata)
        
        engine = DiscoveryEngine()
        query = DiscoveryQuery(domain="planning")
        results = engine.search(query)
        
        assert results.total_found == 5
        assert results.query_timestamp is not None
        assert results.search_duration_ms >= 0


class TestRegistrationValidation:
    """Test registration validation"""
    
    def test_validate_required_interface(self):
        """Test that registration validates orchestrator interface"""
        registry = get_database_registry()
        registry.clear()
        
        # Valid metadata
        metadata = OrchestratorMetadata(
            id="test-1",
            name="Test",
            domain="planning",
            version="1.0",
            capabilities=["test"],
            description="Test",
        )
        
        # Should not raise
        registry.register(metadata)
        assert registry.get("test-1") is not None
    
    def test_duplicate_registration_raises_error(self):
        """Test that duplicate registration raises error"""
        registry = get_database_registry()
        registry.clear()
        
        metadata = OrchestratorMetadata(
            id="test-1",
            name="Test",
            domain="planning",
            version="1.0",
            capabilities=[],
            description="Test",
        )
        
        registry.register(metadata)
        
        # Registering again should raise
        with pytest.raises(ValueError):
            registry.register(metadata)
    
    def test_validation_checks_id_format(self):
        """Test that validation checks ID format"""
        # Invalid ID format (underscore instead of hyphen) should raise
        with pytest.raises(ValueError):
            metadata = OrchestratorMetadata(
                id="test_orch_1",  # Underscore instead of hyphen
                name="Test",
                domain="planning",
                version="1.0",
                capabilities=[],
                description="Test",
            )
    
    def test_validation_checks_domain_exists(self):
        """Test that validation checks domain is valid"""
        # Invalid domain should raise
        with pytest.raises(ValueError):
            metadata = OrchestratorMetadata(
                id="test-1",
                name="Test",
                domain="invalid-domain",
                version="1.0",
                capabilities=[],
                description="Test",
            )


class TestDiscoveryQueryBuilder:
    """Test discovery query building"""
    
    def test_query_with_single_filter(self):
        """Test creating query with single filter"""
        query = DiscoveryQuery(domain="planning")
        assert query.domain == "planning"
        assert query.capability is None
        assert query.version is None
    
    def test_query_with_multiple_filters(self):
        """Test creating query with multiple filters"""
        query = DiscoveryQuery(
            domain="planning",
            capability="execute",
            version="1.0"
        )
        
        assert query.domain == "planning"
        assert query.capability == "execute"
        assert query.version == "1.0"
    
    def test_query_with_no_filters(self):
        """Test creating query with no filters (matches all)"""
        query = DiscoveryQuery()
        
        assert query.domain is None
        assert query.capability is None
        assert query.version is None
    
    def test_query_with_limit(self):
        """Test creating query with result limit"""
        query = DiscoveryQuery(domain="planning", limit=10)
        
        assert query.limit == 10


class TestDiscoveryPerformance:
    """Test discovery performance characteristics"""
    
    def test_discovery_scales_with_orchestrators(self):
        """Test that discovery scales reasonably"""
        registry = get_database_registry()
        registry.clear()
        
        # Register many orchestrators
        for i in range(100):
            metadata = OrchestratorMetadata(
                id=f"orch-{i}",
                name=f"Orchestrator {i}",
                domain="planning" if i % 5 == 0 else "execution",
                version="1.0",
                capabilities=["test"],
                description=f"Orch {i}",
            )
            registry.register(metadata)
        
        engine = DiscoveryEngine()
        import time
        
        start = time.time()
        query = DiscoveryQuery(domain="planning")
        results = engine.search(query)
        elapsed = time.time() - start
        
        # Should be fast even with 100 orchestrators
        assert elapsed < 1.0  # Less than 1 second
        assert len(results.orchestrators) == 20  # 100 / 5

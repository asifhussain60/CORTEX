"""
Tests for OrchestratorRegistry - Dynamic Orchestrator Discovery & Registration

Phase: Task 13.5 - RED Phase
Objective: Create 18 failing tests for orchestrator registry system
Status: RED (all tests should fail - implementation pending)
Author: CORTEX Phase 13 Task 13.5
Created: December 25, 2025
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Type, Optional
import threading
import tempfile


# ============================================================================
# Test Group 1: Registry Initialization (3 tests)
# ============================================================================

class TestRegistryInitialization:
    """Test basic registry initialization."""
    
    def test_registry_initializes_empty(self):
        """Registry should initialize with no orchestrators."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        assert len(registry.list_all()) == 0
        assert registry.count() == 0
    
    def test_registry_has_required_methods(self):
        """Registry should have all required public methods."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        # Check method existence
        assert hasattr(registry, 'register')
        assert hasattr(registry, 'get')
        assert hasattr(registry, 'discover')
        assert hasattr(registry, 'is_available')
        assert hasattr(registry, 'list_all')
        assert hasattr(registry, 'count')
        assert callable(registry.register)
        assert callable(registry.get)
    
    def test_registry_maintains_singleton_pattern(self):
        """Registry should support singleton pattern for global access."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry1 = OrchestratorRegistry.get_instance()
        registry2 = OrchestratorRegistry.get_instance()
        
        assert registry1 is registry2


# ============================================================================
# Test Group 2: Manual Registration (4 tests)
# ============================================================================

class TestManualRegistration:
    """Test manual orchestrator registration."""
    
    def test_register_orchestrator_class(self):
        """Should register orchestrator class by name."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        # Create mock orchestrator class
        class MockOrchestrator(BaseOrchestrator):
            def execute(self, context=None):
                return {"success": True}
        
        registry.register("mock", MockOrchestrator)
        
        assert registry.is_available("mock")
        assert registry.count() == 1
    
    def test_register_duplicate_name_raises_error(self):
        """Registering duplicate name should raise ValueError."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        class Orchestrator1(BaseOrchestrator):
            pass
        
        class Orchestrator2(BaseOrchestrator):
            pass
        
        registry.register("test", Orchestrator1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register("test", Orchestrator2)
    
    def test_register_non_orchestrator_raises_error(self):
        """Registering non-BaseOrchestrator class should raise TypeError."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        class NotAnOrchestrator:
            pass
        
        with pytest.raises(TypeError, match="must inherit from BaseOrchestrator"):
            registry.register("invalid", NotAnOrchestrator)
    
    def test_register_with_metadata(self):
        """Should register orchestrator with metadata (version, capabilities)."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        class TestOrchestrator(BaseOrchestrator):
            pass
        
        registry.register(
            "test",
            TestOrchestrator,
            metadata={"version": "4.0.0", "capabilities": ["planning", "tdd"]}
        )
        
        metadata = registry.get_metadata("test")
        assert metadata["version"] == "4.0.0"
        assert "planning" in metadata["capabilities"]


# ============================================================================
# Test Group 3: Auto-Discovery (5 tests)
# ============================================================================

class TestAutoDiscovery:
    """Test automatic orchestrator discovery."""
    
    def test_discover_orchestrators_in_directory(self):
        """Should discover all orchestrators in given directory."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        # Discover orchestrators in src/orchestrators/
        discovered = registry.discover([Path("src/orchestrators")])
        
        assert discovered > 0
        assert registry.count() > 0
    
    def test_discover_handles_import_errors_gracefully(self):
        """Discovery should skip modules with import errors."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        # Create temp directory with broken module
        with tempfile.TemporaryDirectory() as tmpdir:
            broken_file = Path(tmpdir) / "broken_orchestrator.py"
            broken_file.write_text("import nonexistent_module\nclass Broken: pass")
            
            # Should not raise exception
            discovered = registry.discover([Path(tmpdir)])
            assert discovered == 0  # No valid orchestrators found
    
    def test_discover_extracts_metadata_from_docstrings(self):
        """Should extract version and capabilities from orchestrator docstrings."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create orchestrator with metadata in docstring
            orch_file = Path(tmpdir) / "test_orchestrator.py"
            orch_file.write_text("""
from src.orchestrators.base.base_orchestrator import BaseOrchestrator

class TestOrchestrator(BaseOrchestrator):
    '''
    Test orchestrator with metadata.
    
    Version: 1.0.0
    Capabilities: planning, execution
    '''
    pass
""")
            
            registry.discover([Path(tmpdir)])
            metadata = registry.get_metadata("test")
            
            assert metadata["version"] == "1.0.0"
            assert "planning" in metadata["capabilities"]
    
    def test_discover_respects_plugin_decorator(self):
        """Should recognize @orchestrator_plugin decorator."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            orch_file = Path(tmpdir) / "decorated_orchestrator.py"
            orch_file.write_text("""
from src.orchestrators.base.base_orchestrator import BaseOrchestrator
from src.core.orchestrator_registry import orchestrator_plugin

@orchestrator_plugin("custom_name", version="2.0.0")
class DecoratedOrchestrator(BaseOrchestrator):
    def execute(self, context=None):
        return {"success": True}
""")
            
            registry.discover([Path(tmpdir)])
            
            # Should be registered as "custom_name" not "decorated"
            assert registry.is_available("custom_name")
            assert not registry.is_available("decorated")
    
    def test_discover_multiple_directories(self):
        """Should discover orchestrators from multiple paths."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        paths = [
            Path("src/orchestrators"),
            Path("src/operations/modules")
        ]
        
        discovered = registry.discover(paths)
        
        assert discovered > 0
        assert registry.count() >= discovered


# ============================================================================
# Test Group 4: Lazy Loading (3 tests)
# ============================================================================

class TestLazyLoading:
    """Test lazy orchestrator instantiation."""
    
    def test_get_instantiates_orchestrator_lazily(self):
        """Should instantiate orchestrator only on first get()."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        instantiation_count = 0
        
        class LazyOrchestrator(BaseOrchestrator):
            def __init__(self, config=None, *args, **kwargs):
                nonlocal instantiation_count
                instantiation_count += 1
                super().__init__(config or {}, *args, **kwargs)
            
            def execute(self, **kwargs):
                """Implement abstract execute method."""
                return {"status": "success"}
        
        registry.register("lazy", LazyOrchestrator)
        
        # Not instantiated yet
        assert instantiation_count == 0
        
        # First get() triggers instantiation
        orch1 = registry.get("lazy")
        assert instantiation_count == 1
        
        # Second get() returns cached instance
        orch2 = registry.get("lazy")
        assert instantiation_count == 1
        assert orch1 is orch2
    
    def test_get_returns_none_for_missing_orchestrator(self):
        """get() should return None for non-existent orchestrator."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        
        registry = OrchestratorRegistry()
        
        result = registry.get("nonexistent")
        
        assert result is None
    
    def test_get_passes_initialization_args(self):
        """get() should pass args/kwargs to orchestrator constructor."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        received_args = None
        
        class ConfigurableOrchestrator(BaseOrchestrator):
            def __init__(self, workspace_root: str, **kwargs):
                nonlocal received_args
                received_args = (workspace_root, kwargs)
                super().__init__(workspace_root, **kwargs)
            
            def execute(self, **kwargs):
                """Implement abstract execute method."""
                return {"status": "success"}
        
        registry.register("configurable", ConfigurableOrchestrator)
        
        orch = registry.get("configurable", workspace_root="/test", option="value")
        
        assert received_args[0] == "/test"
        assert received_args[1]["option"] == "value"


# ============================================================================
# Test Group 5: Error Handling (2 tests)
# ============================================================================

class TestErrorHandling:
    """Test registry error handling."""
    
    def test_get_handles_initialization_errors_gracefully(self):
        """get() should return None if orchestrator initialization fails."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        class BrokenOrchestrator(BaseOrchestrator):
            def __init__(self, *args, **kwargs):
                raise RuntimeError("Initialization failed")
            
            def execute(self, **kwargs):
                """Implement abstract execute method."""
                return {"status": "success"}
        
        registry.register("broken", BrokenOrchestrator)
        
        # Should not raise, should return None
        result = registry.get("broken")
        assert result is None
    
    def test_is_available_returns_false_for_broken_orchestrator(self):
        """is_available() should return False for orchestrators that can't initialize."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        class BrokenOrchestrator(BaseOrchestrator):
            def __init__(self, config=None, *args, **kwargs):
                raise ImportError("Missing dependency")
            
            def execute(self, **kwargs):
                """Implement abstract execute method."""
                return {"status": "success"}
        
        registry.register("broken", BrokenOrchestrator)
        
        # Registered but not available (can't instantiate)
        assert not registry.is_available("broken")


# ============================================================================
# Test Group 6: Thread Safety (1 test)
# ============================================================================

class TestThreadSafety:
    """Test registry thread safety."""
    
    def test_concurrent_get_calls_are_thread_safe(self):
        """Concurrent get() calls should be thread-safe (no race conditions)."""
        from src.core.orchestrator_registry import OrchestratorRegistry
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        registry = OrchestratorRegistry()
        
        instantiation_count = 0
        
        class ThreadSafeOrchestrator(BaseOrchestrator):
            def __init__(self, config=None, *args, **kwargs):
                nonlocal instantiation_count
                instantiation_count += 1
                super().__init__(config or {}, *args, **kwargs)
            
            def execute(self, **kwargs):
                """Implement abstract execute method."""
                return {"status": "success"}
        
        registry.register("threadsafe", ThreadSafeOrchestrator)
        
        instances = []
        
        def get_orchestrator():
            instances.append(registry.get("threadsafe"))
        
        # Create 10 threads calling get() simultaneously
        threads = [threading.Thread(target=get_orchestrator) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should instantiate only once
        assert instantiation_count == 1
        
        # All threads should get same instance
        assert all(inst is instances[0] for inst in instances)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def clean_registry():
    """Provide clean registry for each test."""
    from src.core.orchestrator_registry import OrchestratorRegistry
    
    # Clear singleton instance
    if hasattr(OrchestratorRegistry, '_instance'):
        OrchestratorRegistry._instance = None
    
    registry = OrchestratorRegistry()
    yield registry
    
    # Cleanup
    if hasattr(OrchestratorRegistry, '_instance'):
        OrchestratorRegistry._instance = None

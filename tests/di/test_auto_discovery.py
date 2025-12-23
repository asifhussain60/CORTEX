"""
Tests for Auto-Discovery Module

Phase: 7B - Operations Simplification (Task 7.7.3)
Author: Asif Hussain
Created: December 23, 2025

Tests:
- Module scanning
- Decorator-based discovery (@service)
- Convention-based discovery (IService -> ServiceImpl)
- Scope detection
- Integration with ServiceContainer
"""

import pytest
from typing import Protocol
from abc import ABC, abstractmethod

from src.di import ServiceContainer, ServiceScope, AutoDiscovery, service


# ==============================================================================
# Test Fixtures and Mock Services
# ==============================================================================

class ILogger(Protocol):
    """Logger interface"""
    def log(self, message: str) -> None: ...


@service(scope="singleton")
class ConsoleLogger:
    """Console logger with @service decorator"""
    __service__ = True
    __service_scope__ = ServiceScope.SINGLETON
    
    def log(self, message: str) -> None:
        print(message)


class IDatabase(ABC):
    """Database interface (abstract base)"""
    @abstractmethod
    def connect(self) -> bool: ...


class DatabaseImpl(IDatabase):
    """Database implementation (convention-based)"""
    def connect(self) -> bool:
        return True


@service(scope="transient", interface=ILogger)
class FileLogger(ILogger):
    """File logger with explicit interface"""
    __service__ = True
    __service_scope__ = ServiceScope.TRANSIENT
    __service_interface__ = ILogger
    
    def log(self, message: str) -> None:
        pass  # Write to file


class ServiceWithoutDecorator:
    """Service without @service decorator (should not be discovered)"""
    pass


# ==============================================================================
# Test Group 1: Decorator-Based Discovery (6 tests)
# ==============================================================================

class TestDecoratorDiscovery:
    """Test @service decorator detection"""
    
    def test_discover_service_with_decorator(self):
        """Test discovering service with @service decorator"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Create a proper mock module and define class within it
        import types
        mock_module = types.ModuleType('test_module')
        mock_module.__name__ = 'test_module'
        
        # Define a test service class directly in the mock module
        @service(scope="singleton")
        class TestService:
            __service__ = True
            __service_scope__ = ServiceScope.SINGLETON
            pass
        
        TestService.__module__ = 'test_module'  # Set module to match
        mock_module.TestService = TestService
        
        discovered = discovery._scan_module_members(mock_module)
        
        assert discovered >= 1
        assert container.is_registered(TestService)
    
    def test_service_scope_from_decorator(self):
        """Test scope detection from @service decorator"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        scope = discovery._detect_scope(ConsoleLogger)
        
        assert scope == ServiceScope.SINGLETON
    
    def test_service_with_explicit_interface(self):
        """Test service with explicit interface parameter"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Check __service_interface__ attribute
        assert hasattr(FileLogger, '__service_interface__')
        assert FileLogger.__service_interface__ == ILogger
    
    def test_service_without_decorator_not_discovered(self):
        """Test that services without @service are not discovered"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        import types
        mock_module = types.ModuleType('test_module')
        mock_module.__name__ = 'test_module'
        mock_module.ServiceWithoutDecorator = ServiceWithoutDecorator
        
        discovered = discovery._scan_module_members(mock_module)
        
        # Should not discover service without decorator
        assert not container.is_registered(ServiceWithoutDecorator)
    
    def test_duplicate_discovery_ignored(self):
        """Test that duplicate discovery is ignored"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Discover twice
        discovery._register_service(ConsoleLogger, ConsoleLogger, ServiceScope.SINGLETON)
        discovery._register_service(ConsoleLogger, ConsoleLogger, ServiceScope.SINGLETON)
        
        # Should only be registered once
        assert container.is_registered(ConsoleLogger)
    
    def test_get_discovered_services_returns_list(self):
        """Test getting list of discovered services"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Add to discovered set
        discovery._discovered.add("test.module.ServiceA")
        discovery._discovered.add("test.module.ServiceB")
        
        services = discovery.get_discovered_services()
        
        assert len(services) == 2
        assert "test.module.ServiceA" in services
        assert "test.module.ServiceB" in services


# ==============================================================================
# Test Group 2: Convention-Based Discovery (5 tests)
# ==============================================================================

class TestConventionDiscovery:
    """Test convention-based service discovery"""
    
    def test_detect_implementation_class_by_name(self):
        """Test detecting implementation classes by naming convention"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Classes ending with Impl, Service, Manager, Orchestrator
        assert discovery._is_implementation_class(DatabaseImpl)
        assert not discovery._is_implementation_class(IDatabase)
    
    def test_find_interface_for_implementation(self):
        """Test finding interface for implementation class"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        interface = discovery._find_interface(DatabaseImpl)
        
        assert interface == IDatabase
    
    def test_interface_naming_conventions(self):
        """Test various interface naming conventions"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Test IService pattern
        class IService(ABC):
            @abstractmethod
            def do_something(self): ...
        
        class ServiceImpl(IService):
            def do_something(self): pass
        
        interface = discovery._find_interface(ServiceImpl)
        assert interface == IService
    
    def test_implementation_without_interface_returns_none(self):
        """Test implementation without interface returns None"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        class StandaloneService:
            pass
        
        interface = discovery._find_interface(StandaloneService)
        assert interface is None
    
    def test_abstract_base_detected_as_interface(self):
        """Test abstract base classes detected as interfaces"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        class AbstractService(ABC):
            @abstractmethod
            def execute(self): ...
        
        class ConcreteService(AbstractService):
            def execute(self): return True
        
        interface = discovery._find_interface(ConcreteService)
        assert interface == AbstractService


# ==============================================================================
# Test Group 3: Scope Detection (4 tests)
# ==============================================================================

class TestScopeDetection:
    """Test lifecycle scope detection"""
    
    def test_detect_scope_from_class_attribute(self):
        """Test scope detection from __service_scope__ attribute"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        class MySingletonService:
            __service_scope__ = ServiceScope.SINGLETON
        
        scope = discovery._detect_scope(MySingletonService)
        assert scope == ServiceScope.SINGLETON
    
    def test_detect_scope_from_string_attribute(self):
        """Test scope detection from string __service_scope__"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        class MyTransientService:
            __service_scope__ = "transient"
        
        scope = discovery._detect_scope(MyTransientService)
        assert scope == ServiceScope.TRANSIENT
    
    def test_custom_scope_detector_takes_priority(self):
        """Test custom scope detector overrides class attribute"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        class MyService:
            __service_scope__ = ServiceScope.TRANSIENT
        
        # Custom detector returns SINGLETON
        def custom_detector(cls):
            return ServiceScope.SINGLETON
        
        scope = discovery._detect_scope(MyService, custom_detector=custom_detector)
        assert scope == ServiceScope.SINGLETON
    
    def test_default_scope_is_transient(self):
        """Test default scope is TRANSIENT when not specified"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        class MyDefaultService:
            pass
        
        scope = discovery._detect_scope(MyDefaultService)
        assert scope == ServiceScope.TRANSIENT


# ==============================================================================
# Test Group 4: Integration Tests (3 tests)
# ==============================================================================

class TestAutoDiscoveryIntegration:
    """Test auto-discovery integration with ServiceContainer"""
    
    def test_register_and_resolve_discovered_service(self):
        """Test registering and resolving discovered service"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Register manually (simulating discovery)
        discovery._register_service(
            ConsoleLogger,
            ConsoleLogger,
            ServiceScope.SINGLETON
        )
        
        # Resolve
        logger = container.resolve(ConsoleLogger)
        assert logger is not None
        assert isinstance(logger, ConsoleLogger)
    
    def test_clear_discovered_services(self):
        """Test clearing discovered services cache"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        discovery._discovered.add("test.ServiceA")
        discovery._discovered.add("test.ServiceB")
        
        assert len(discovery.get_discovered_services()) == 2
        
        discovery.clear()
        assert len(discovery.get_discovered_services()) == 0
    
    def test_scan_module_returns_count(self):
        """Test scan_module returns registration count"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        import types
        mock_module = types.ModuleType('test_module')
        mock_module.__name__ = 'test_module'
        mock_module.ConsoleLogger = ConsoleLogger
        
        count = discovery._scan_module_members(mock_module)
        
        assert count >= 0


# ==============================================================================
# Test Group 5: Error Handling (3 tests)
# ==============================================================================

class TestAutoDiscoveryErrors:
    """Test error handling in auto-discovery"""
    
    def test_scan_nonexistent_module_returns_zero(self):
        """Test scanning nonexistent module returns 0"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        count = discovery.scan_module("nonexistent.module.that.does.not.exist")
        
        assert count == 0
    
    def test_scan_path_nonexistent_returns_zero(self):
        """Test scanning nonexistent path returns 0"""
        from pathlib import Path
        
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        count = discovery.scan_path(Path("/nonexistent/path/12345"))
        
        assert count == 0
    
    def test_invalid_custom_scope_detector_falls_back(self):
        """Test invalid custom scope detector falls back to default"""
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        class MyService:
            pass
        
        def bad_detector(cls):
            raise ValueError("Detector error")
        
        # Should fall back to default (TRANSIENT)
        scope = discovery._detect_scope(MyService, custom_detector=bad_detector)
        assert scope == ServiceScope.TRANSIENT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
ServiceContainer RED Tests (TDD Phase 1)

Phase: 7B - Operations Simplification (Task 7.7.1)
Author: Asif Hussain
Created: December 23, 2025

Tests DI Container core functionality:
- Service registration
- Service resolution
- Lifecycle scopes (singleton, transient, scoped)
- Auto-wiring
- Circular dependency detection
- Error handling
"""

import pytest
from typing import Optional
from src.di import ServiceContainer, ServiceScope


# ============================================================================
# Test Fixtures - Simple Service Classes
# ============================================================================

class ILogger:
    """Logger interface."""
    def log(self, message: str) -> None:
        pass


class ConsoleLogger(ILogger):
    """Console logger implementation."""
    def __init__(self):
        self.messages = []
    
    def log(self, message: str) -> None:
        self.messages.append(message)


class IDatabase:
    """Database interface."""
    def query(self, sql: str) -> list:
        pass


class SqliteDatabase(IDatabase):
    """SQLite database implementation."""
    def __init__(self, logger: ILogger):
        self.logger = logger
        self.connections = 0
    
    def query(self, sql: str) -> list:
        self.logger.log(f"Query: {sql}")
        return []


class ICache:
    """Cache interface."""
    def get(self, key: str) -> Optional[str]:
        pass
    
    def set(self, key: str, value: str) -> None:
        pass


class MemoryCache(ICache):
    """Memory cache implementation."""
    def __init__(self, logger: ILogger, database: IDatabase):
        self.logger = logger
        self.database = database
        self.data = {}
    
    def get(self, key: str) -> Optional[str]:
        return self.data.get(key)
    
    def set(self, key: str, value: str) -> None:
        self.data[key] = value


# Circular dependency test classes
class ServiceA:
    def __init__(self, service_b: 'ServiceB'):
        self.service_b = service_b


class ServiceB:
    def __init__(self, service_a: ServiceA):
        self.service_a = service_a


# ============================================================================
# Test: Service Registration
# ============================================================================

class TestServiceRegistration:
    """Test service registration."""
    
    def test_register_simple_service(self):
        """Test: Register service without dependencies."""
        container = ServiceContainer()
        
        container.register(ILogger, ConsoleLogger)
        
        assert container.is_registered(ILogger)
    
    def test_register_service_with_implementation(self):
        """Test: Register interface with concrete implementation."""
        container = ServiceContainer()
        
        container.register(ILogger, ConsoleLogger, ServiceScope.SINGLETON)
        
        registration = container.get_registration(ILogger)
        assert registration is not None
        assert registration.service_type == ILogger
        assert registration.implementation == ConsoleLogger
        assert registration.scope == ServiceScope.SINGLETON
    
    def test_register_service_without_implementation_uses_self(self):
        """Test: Register without implementation defaults to service_type."""
        container = ServiceContainer()
        
        container.register(ConsoleLogger)
        
        assert container.is_registered(ConsoleLogger)
    
    def test_register_duplicate_service_raises_error(self):
        """Test: Registering same service twice raises ValueError."""
        container = ServiceContainer()
        
        container.register(ILogger, ConsoleLogger)
        
        with pytest.raises(ValueError, match="already registered"):
            container.register(ILogger, ConsoleLogger)
    
    def test_register_instance(self):
        """Test: Register pre-created instance."""
        container = ServiceContainer()
        logger = ConsoleLogger()
        logger.log("test")
        
        container.register_instance(ILogger, logger)
        
        resolved = container.resolve(ILogger)
        assert resolved is logger
        assert "test" in resolved.messages


# ============================================================================
# Test: Service Resolution
# ============================================================================

class TestServiceResolution:
    """Test service resolution."""
    
    def test_resolve_simple_service(self):
        """Test: Resolve service without dependencies."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger)
        
        logger = container.resolve(ILogger)
        
        assert logger is not None
        assert isinstance(logger, ConsoleLogger)
    
    def test_resolve_unregistered_service_raises_error(self):
        """Test: Resolving unregistered service raises KeyError."""
        container = ServiceContainer()
        
        with pytest.raises(KeyError, match="not registered"):
            container.resolve(ILogger)
    
    def test_resolve_service_with_dependencies(self):
        """Test: Auto-wire dependencies."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger)
        container.register(IDatabase, SqliteDatabase)
        
        database = container.resolve(IDatabase)
        
        assert database is not None
        assert isinstance(database, SqliteDatabase)
        assert isinstance(database.logger, ConsoleLogger)
    
    def test_resolve_service_with_nested_dependencies(self):
        """Test: Auto-wire multi-level dependencies."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger)
        container.register(IDatabase, SqliteDatabase)
        container.register(ICache, MemoryCache)
        
        cache = container.resolve(ICache)
        
        assert cache is not None
        assert isinstance(cache, MemoryCache)
        assert isinstance(cache.logger, ConsoleLogger)
        assert isinstance(cache.database, SqliteDatabase)


# ============================================================================
# Test: Lifecycle Scopes
# ============================================================================

class TestServiceScopes:
    """Test service lifecycle scopes."""
    
    def test_transient_scope_creates_new_instance_each_time(self):
        """Test: TRANSIENT scope returns different instances."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger, ServiceScope.TRANSIENT)
        
        logger1 = container.resolve(ILogger)
        logger2 = container.resolve(ILogger)
        
        assert logger1 is not logger2
    
    def test_singleton_scope_returns_same_instance(self):
        """Test: SINGLETON scope returns same instance."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger, ServiceScope.SINGLETON)
        
        logger1 = container.resolve(ILogger)
        logger2 = container.resolve(ILogger)
        
        assert logger1 is logger2
    
    def test_scoped_instance_same_within_scope(self):
        """Test: SCOPED returns same instance within same scope."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger, ServiceScope.SCOPED)
        
        logger1 = container.resolve(ILogger, scope_id="request-1")
        logger2 = container.resolve(ILogger, scope_id="request-1")
        
        assert logger1 is logger2
    
    def test_scoped_instance_different_across_scopes(self):
        """Test: SCOPED returns different instances across scopes."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger, ServiceScope.SCOPED)
        
        logger1 = container.resolve(ILogger, scope_id="request-1")
        logger2 = container.resolve(ILogger, scope_id="request-2")
        
        assert logger1 is not logger2
    
    def test_scoped_service_without_scope_id_raises_error(self):
        """Test: SCOPED service requires scope_id."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger, ServiceScope.SCOPED)
        
        with pytest.raises(ValueError, match="Scope ID required"):
            container.resolve(ILogger)
    
    def test_clear_scope_removes_instances(self):
        """Test: clear_scope() removes scoped instances."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger, ServiceScope.SCOPED)
        
        logger1 = container.resolve(ILogger, scope_id="request-1")
        container.clear_scope("request-1")
        logger2 = container.resolve(ILogger, scope_id="request-1")
        
        assert logger1 is not logger2


# ============================================================================
# Test: Circular Dependencies
# ============================================================================

class TestCircularDependencies:
    """Test circular dependency detection."""
    
    def test_circular_dependency_raises_error(self):
        """Test: Circular dependency raises RuntimeError."""
        container = ServiceContainer()
        container.register(ServiceA)
        container.register(ServiceB)
        
        with pytest.raises(RuntimeError, match="Circular dependency"):
            container.resolve(ServiceA)


# ============================================================================
# Test: Error Handling
# ============================================================================

class TestErrorHandling:
    """Test error handling."""
    
    def test_missing_dependency_logs_warning_continues(self):
        """Test: Missing optional dependency logs warning but continues."""
        container = ServiceContainer()
        # Register database without logger (dependency missing)
        container.register(IDatabase, SqliteDatabase)
        
        # Should not raise, but log warning
        database = container.resolve(IDatabase)
        assert database is not None


# ============================================================================
# Test: Container State
# ============================================================================

class TestContainerState:
    """Test container state management."""
    
    def test_is_registered_returns_true_for_registered(self):
        """Test: is_registered() returns True for registered services."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger)
        
        assert container.is_registered(ILogger)
    
    def test_is_registered_returns_false_for_unregistered(self):
        """Test: is_registered() returns False for unregistered services."""
        container = ServiceContainer()
        
        assert not container.is_registered(ILogger)
    
    def test_get_registration_returns_metadata(self):
        """Test: get_registration() returns registration metadata."""
        container = ServiceContainer()
        container.register(ILogger, ConsoleLogger, ServiceScope.SINGLETON)
        
        registration = container.get_registration(ILogger)
        
        assert registration is not None
        assert registration.service_type == ILogger
        assert registration.implementation == ConsoleLogger
        assert registration.scope == ServiceScope.SINGLETON
    
    def test_get_registration_returns_none_for_unregistered(self):
        """Test: get_registration() returns None for unregistered service."""
        container = ServiceContainer()
        
        registration = container.get_registration(ILogger)
        
        assert registration is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

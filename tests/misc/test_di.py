"""
Tests for Dependency Injection system

Test coverage:
- Container initialization and singleton behavior
- Provider registration and resolution
- Decorator functionality
- Dependency wiring
"""

import pytest
from unittest.mock import Mock, patch

from src.di import CortexContainer, get_container, orchestrator, injectable
from src.di.container import reset_container
from dependency_injector.wiring import Provide


class TestCortexContainer:
    """Test suite for CortexContainer"""
    
    def setup_method(self):
        """Reset container before each test"""
        reset_container()
    
    def teardown_method(self):
        """Cleanup after each test"""
        reset_container()
    
    def test_container_singleton(self):
        """Test that get_container returns singleton"""
        container1 = get_container()
        container2 = get_container()
        
        assert container1 is container2
    
    def test_container_has_config_provider(self):
        """Test that container has config provider"""
        container = get_container()
        
        assert hasattr(container, 'config')
        assert container.config is not None
    
    def test_container_has_logger_factory(self):
        """Test that container has logger factory"""
        container = get_container()
        
        assert hasattr(container, 'logger_factory')
        assert container.logger_factory is not None
    
    def test_container_has_template_manager(self):
        """Test that container has template manager"""
        container = get_container()
        
        assert hasattr(container, 'template_manager')
        assert container.template_manager is not None
    
    def test_container_has_mcp_gateway(self):
        """Test that container has MCP gateway"""
        container = get_container()
        
        assert hasattr(container, 'mcp_gateway')
        assert container.mcp_gateway is not None
    
    def test_reset_container(self):
        """Test that reset_container clears singleton"""
        container1 = get_container()
        reset_container()
        container2 = get_container()
        
        assert container1 is not container2


class TestOrchestratorDecorator:
    """Test suite for @orchestrator decorator"""
    
    def setup_method(self):
        """Reset container before each test"""
        reset_container()
    
    def teardown_method(self):
        """Cleanup after each test"""
        reset_container()
    
    def test_orchestrator_decorator_applies(self):
        """Test that @orchestrator decorator can be applied"""
        
        @orchestrator
        class TestOrchestrator:
            def __init__(self):
                self.name = "test"
        
        # Should not raise
        instance = TestOrchestrator()
        assert instance.name == "test"
    
    def test_orchestrator_with_dependency_injection(self):
        """Test orchestrator with DI (mock dependencies)"""
        
        # Note: Full DI testing requires wiring, which is complex
        # This test validates the decorator doesn't break basic functionality
        
        @orchestrator
        class TestOrchestrator:
            def __init__(self, config=None):
                self.config = config
        
        instance = TestOrchestrator(config={"test": "value"})
        assert instance.config == {"test": "value"}


class TestInjectableDecorator:
    """Test suite for @injectable decorator"""
    
    def test_injectable_decorator_applies(self):
        """Test that @injectable decorator can be applied"""
        
        @injectable
        def test_function():
            return "test"
        
        result = test_function()
        assert result == "test"
    
    def test_injectable_with_parameters(self):
        """Test injectable with parameters"""
        
        @injectable
        def test_function(value: str = "default"):
            return f"value: {value}"
        
        result = test_function(value="custom")
        assert result == "value: custom"


class TestDIIntegration:
    """Integration tests for DI system"""
    
    def setup_method(self):
        """Reset container before each test"""
        reset_container()
    
    def teardown_method(self):
        """Cleanup after each test"""
        reset_container()
    
    def test_container_providers_are_accessible(self):
        """Test that all providers can be accessed"""
        container = get_container()
        
        # These should not raise
        config_provider = container.config
        logger_provider = container.logger_factory
        template_provider = container.template_manager
        mcp_provider = container.mcp_gateway
        
        assert config_provider is not None
        assert logger_provider is not None
        assert template_provider is not None
        assert mcp_provider is not None

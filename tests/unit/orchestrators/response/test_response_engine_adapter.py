"""
Test suite for Response Engine Adapter (ENH-082 Wave 2 Stage 3).

Tests for AC-ENH082-W2-S3-001: ResponseEngineAdapter
- Mixin pattern integration
- Feature flag control per orchestrator
- Post-domain-logic composition hook
- Graceful fallback behavior
- Decorator-based enablement
- Runtime migration support

Total: 15 comprehensive tests

Author: Asif Hussain
Created: 2026-02-12
AC-ID: AC-ENH082-W2-S3-001
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from cortex.core.result import Ok, Err
from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.response.response_engine_adapter import (
    ResponseEngineMixin,
    OrchestratorResponseConfig,
    enable_response_engine_for_orchestrator,
    migrate_orchestrator_to_response_engine,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================


class MockOrchestrator(ResponseEngineMixin):
    """Mock orchestrator with ResponseEngineMixin."""
    
    def __init__(self, enable_response_engine=False):
        self._init_response_engine(
            intent_type=IntentType.IMPLEMENT,
            orchestrator_name="MockOrchestrator",
            enable=enable_response_engine
        )


@pytest.fixture
def orchestrator_with_engine():
    """Orchestrator with response engine enabled."""
    return MockOrchestrator(enable_response_engine=True)


@pytest.fixture
def orchestrator_without_engine():
    """Orchestrator with response engine disabled."""
    return MockOrchestrator(enable_response_engine=False)


# ============================================================================
# TEST: OrchestratorResponseConfig
# ============================================================================


class TestOrchestratorResponseConfig:
    """Test configuration dataclass."""

    def test_default_config_disabled(self):
        """Test default configuration has response engine disabled."""
        config = OrchestratorResponseConfig()
        
        assert config.enable_response_engine is False
        assert config.fallback_to_default is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = OrchestratorResponseConfig(
            enable_response_engine=True,
            intent_type=IntentType.REFACTOR,
            orchestrator_name="TestOrch",
            log_composition=True
        )
        
        assert config.enable_response_engine is True
        assert config.intent_type == IntentType.REFACTOR
        assert config.orchestrator_name == "TestOrch"
        assert config.log_composition is True


# ============================================================================
# TEST: ResponseEngineMixin
# ============================================================================


class TestResponseEngineMixin:
    """Test mixin pattern integration."""

    def test_mixin_initialization(self, orchestrator_with_engine):
        """Test mixin initializes response engine."""
        assert hasattr(orchestrator_with_engine, '_response_engine')
        assert hasattr(orchestrator_with_engine, '_response_config')
        assert orchestrator_with_engine._response_config.enable_response_engine is True

    def test_mixin_disabled_by_default(self, orchestrator_without_engine):
        """Test mixin disabled by default."""
        assert orchestrator_without_engine._response_config.enable_response_engine is False

    def test_compose_response_disabled_returns_original(self, orchestrator_without_engine):
        """Test compose_response returns original result when disabled."""
        original_result = Ok({"status": "success"})
        
        result = orchestrator_without_engine._compose_response(
            domain_result=original_result,
            context={}
        )
        
        # Should return original result unchanged
        assert result == original_result

    def test_compose_response_enabled_calls_engine(self, orchestrator_with_engine):
        """Test compose_response calls UnifiedResponseEngine when enabled."""
        domain_result = Ok({"test_count": 10, "coverage": 85})
        context = {"file_path": "app.py"}
        
        result = orchestrator_with_engine._compose_response(
            domain_result=domain_result,
            context=context
        )
        
        # Should return composed result
        assert hasattr(result, 'value') or isinstance(result, Ok)
        # Check for composition indicators
        if hasattr(result, 'value'):
            value = result.value
            if isinstance(value, dict):
                assert "composed_via" in value or "response" in value

    def test_compose_response_error_passthrough(self, orchestrator_with_engine):
        """Test compose_response passes through errors unchanged."""
        error_result = Err("Domain execution failed")
        
        result = orchestrator_with_engine._compose_response(
            domain_result=error_result,
            context={}
        )
        
        # Should return error unchanged
        assert result == error_result

    def test_compose_response_fallback_on_exception(self, orchestrator_with_engine):
        """Test compose_response falls back gracefully on exception."""
        # Create result that will cause composition to fail
        domain_result = Ok({"invalid": "data"})
        
        with patch.object(orchestrator_with_engine._response_engine, 'compose',
                         side_effect=Exception("Composition failed")):
            result = orchestrator_with_engine._compose_response(
                domain_result=domain_result,
                context={}
            )
        
        # Should fall back to original result
        assert result == domain_result


# ============================================================================
# TEST: Decorator-Based Enablement
# ============================================================================


class TestDecoratorEnablement:
    """Test @enable_response_engine_for_orchestrator decorator."""

    def test_decorator_adds_mixin(self):
        """Test decorator adds ResponseEngineMixin to class."""
        class TestOrchestrator:
            def __init__(self):
                pass
        
        # Apply decorator
        enhanced_class = enable_response_engine_for_orchestrator(
            TestOrchestrator,
            intent_type=IntentType.IMPLEMENT,
            orchestrator_name="TestOrchestrator"
        )
        
        # Check mixin added
        assert ResponseEngineMixin in enhanced_class.__bases__

    def test_decorator_auto_configures(self):
        """Test decorator auto-configures response engine."""
        class TestOrchestrator:
            def __init__(self):
                pass
        
        # Apply decorator
        enhanced_class = enable_response_engine_for_orchestrator(
            TestOrchestrator,
            intent_type=IntentType.REFACTOR,
            orchestrator_name="TestOrch"
        )
        
        # Create instance
        instance = enhanced_class()
        
        # Check configuration
        assert hasattr(instance, '_response_config')
        assert instance._response_config.enable_response_engine is True
        assert instance._response_config.intent_type == IntentType.REFACTOR


# ============================================================================
# TEST: Runtime Migration
# ============================================================================


class TestRuntimeMigration:
    """Test runtime migration helper."""

    def test_runtime_migration_adds_methods(self):
        """Test runtime migration adds mixin methods to instance."""
        class PlainOrchestrator:
            pass
        
        instance = PlainOrchestrator()
        
        # Before migration
        assert not hasattr(instance, '_init_response_engine')
        assert not hasattr(instance, '_compose_response')
        
        # Migrate
        migrate_orchestrator_to_response_engine(
            instance,
            intent_type=IntentType.IMPLEMENT,
            enable=False
        )
        
        # After migration
        assert hasattr(instance, '_init_response_engine')
        assert hasattr(instance, '_compose_response')
        assert hasattr(instance, '_response_config')

    def test_runtime_migration_respects_enable_flag(self):
        """Test runtime migration respects enable flag."""
        class PlainOrchestrator:
            pass
        
        # Test with enable=False
        instance1 = PlainOrchestrator()
        migrate_orchestrator_to_response_engine(
            instance1,
            intent_type=IntentType.IMPLEMENT,
            enable=False
        )
        assert hasattr(instance1, '_response_config')
        assert instance1._response_config.enable_response_engine is False  # type: ignore
        
        # Test with enable=True
        instance2 = PlainOrchestrator()
        migrate_orchestrator_to_response_engine(
            instance2,
            intent_type=IntentType.IMPLEMENT,
            enable=True
        )
        assert hasattr(instance2, '_response_config')
        assert instance2._response_config.enable_response_engine is True  # type: ignore


# ============================================================================
# TEST: Integration Scenarios
# ============================================================================


class TestIntegrationScenarios:
    """Test integration scenarios."""

    def test_end_to_end_enabled_flow(self, orchestrator_with_engine):
        """Test end-to-end flow with response engine enabled."""
        # Simulate domain execution result
        domain_result = Ok({
            "tests_passed": 10,
            "coverage": 90,
            "file_path": "test.py"
        })
        
        context = {
            "user_request": "Implement feature X",
            "intent": IntentType.IMPLEMENT
        }
        
        # Compose response
        result = orchestrator_with_engine._compose_response(
            domain_result=domain_result,
            context=context
        )
        
        # Should return composed result
        assert result is not None

    def test_backward_compatibility_disabled(self, orchestrator_without_engine):
        """Test backward compatibility when engine disabled."""
        domain_result = Ok({"status": "success"})
        
        result = orchestrator_without_engine._compose_response(
            domain_result=domain_result,
            context={}
        )
        
        # Should behave exactly as before (no modification)
        assert result == domain_result

    def test_multiple_orchestrators_independent_config(self):
        """Test multiple orchestrators can have independent configs."""
        orch1 = MockOrchestrator(enable_response_engine=True)
        orch2 = MockOrchestrator(enable_response_engine=False)
        
        # Both should work independently
        assert orch1._response_config.enable_response_engine is True
        assert orch2._response_config.enable_response_engine is False

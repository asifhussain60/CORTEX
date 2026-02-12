"""
Test suite for Unified Response Engine (ENH-082 Wave 2).

Tests for AC-ENH082-W2-001: UnifiedResponseEngine
- Configuration management (feature flags)
- Intent → Role mapping (15 intent types)
- Template fusion (role + orchestrator)
- Variable auto-binding (80%+ automatic)
- Response composition (end-to-end)
- Fallback behavior (graceful degradation)
- Error handling (missing templates)

Total: 25 comprehensive tests

Author: Asif Hussain
Created: 2026-02-12
AC-ID: AC-ENH082-W2-001
"""

import pytest
from typing import Dict, Any

from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.response.unified_response_engine import (
    ResponseEngineConfig,
    IntentRoleMapper,
    FusedTemplate,
    TemplateFusionEngine,
    VariableAutoBinder,
    UnifiedResponseEngine,
)
from cortex.orchestrators.response.multi_role_response_engine import Role


# ============================================================================
# TEST: ResponseEngineConfig
# ============================================================================


class TestResponseEngineConfig:
    """Test configuration management for response engine."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ResponseEngineConfig()
        
        assert config.enable_role_detection is True
        assert config.enable_template_fusion is True
        assert config.enable_variable_binding is True
        assert config.fallback_to_orchestrator is True
        assert config.feature_flag_enabled is False  # Disabled by default
        assert config.log_composition_steps is False

    def test_custom_config(self):
        """Test custom configuration."""
        config = ResponseEngineConfig(
            enable_role_detection=False,
            feature_flag_enabled=True,
            log_composition_steps=True
        )
        
        assert config.enable_role_detection is False
        assert config.feature_flag_enabled is True
        assert config.log_composition_steps is True

    def test_config_feature_flag_safety(self):
        """Test feature flag defaults to False for safety."""
        config = ResponseEngineConfig()
        
        # Safety: Feature should be disabled by default
        assert config.feature_flag_enabled is False


# ============================================================================
# TEST: IntentRoleMapper
# ============================================================================


class TestIntentRoleMapper:
    """Test intent to role mapping."""

    def test_implement_maps_to_engineer(self):
        """Test IMPLEMENT intent maps to ENGINEER role."""
        role = IntentRoleMapper.get_role(IntentType.IMPLEMENT)
        assert role == Role.ENGINEER

    def test_fix_maps_to_engineer(self):
        """Test FIX intent maps to ENGINEER role."""
        role = IntentRoleMapper.get_role(IntentType.FIX)
        assert role == Role.ENGINEER

    def test_refactor_maps_to_engineer(self):
        """Test REFACTOR intent maps to ENGINEER role."""
        role = IntentRoleMapper.get_role(IntentType.REFACTOR)
        assert role == Role.ENGINEER

    def test_analyze_maps_to_cto(self):
        """Test ANALYZE intent maps to CTO role."""
        role = IntentRoleMapper.get_role(IntentType.ANALYZE)
        assert role == Role.CTO

    def test_plan_maps_to_product_manager(self):
        """Test PLAN intent maps to PRODUCT_MANAGER role."""
        role = IntentRoleMapper.get_role(IntentType.PLAN)
        assert role == Role.PRODUCT_MANAGER

    def test_governance_maps_to_security(self):
        """Test GOVERNANCE intent maps to SECURITY_OFFICER role."""
        role = IntentRoleMapper.get_role(IntentType.GOVERNANCE)
        assert role == Role.SECURITY_OFFICER

    def test_query_maps_to_business(self):
        """Test QUERY intent maps to BUSINESS_LEAD role."""
        role = IntentRoleMapper.get_role(IntentType.QUERY)
        assert role == Role.BUSINESS_LEAD

    def test_unknown_intent_defaults_to_engineer(self):
        """Test unknown intent defaults to ENGINEER role."""
        role = IntentRoleMapper.get_role(IntentType.UNKNOWN)
        assert role == Role.ENGINEER

    def test_supports_intent_known(self):
        """Test supports_intent returns True for known intent."""
        assert IntentRoleMapper.supports_intent(IntentType.IMPLEMENT) is True

    def test_supports_intent_unknown(self):
        """Test supports_intent returns False for unknown intent."""
        assert IntentRoleMapper.supports_intent(IntentType.UNKNOWN) is False


# ============================================================================
# TEST: VariableAutoBinder
# ============================================================================


class TestVariableAutoBinder:
    """Test automatic variable binding from context."""

    def test_direct_match_binding(self):
        """Test direct variable name match."""
        binder = VariableAutoBinder()
        
        variables = ["file_path", "module_name"]
        context = {"file_path": "app.py", "module_name": "core"}
        
        bound = binder.bind(variables, context)
        
        assert bound["file_path"] == "app.py"
        assert bound["module_name"] == "core"

    def test_mapped_key_binding(self):
        """Test binding via mapped alternative keys."""
        binder = VariableAutoBinder()
        
        variables = ["file_path"]
        context = {"target_file": "test.py"}  # Alternative key
        
        bound = binder.bind(variables, context)
        
        assert bound["file_path"] == "test.py"

    def test_multiple_alternatives_first_match(self):
        """Test multiple alternatives - takes first match."""
        binder = VariableAutoBinder()
        
        variables = ["file_path"]
        context = {"file": "app.py", "path": "src/app.py"}
        
        bound = binder.bind(variables, context)
        
        # Should match first alternative
        assert "file_path" in bound

    def test_missing_variable_not_bound(self):
        """Test missing variable is not bound."""
        binder = VariableAutoBinder()
        
        variables = ["missing_var"]
        context = {"other_var": "value"}
        
        bound = binder.bind(variables, context)
        
        assert "missing_var" not in bound

    def test_empty_context(self):
        """Test binding with empty context."""
        binder = VariableAutoBinder()
        
        variables = ["file_path"]
        context = {}
        
        bound = binder.bind(variables, context)
        
        assert len(bound) == 0

    def test_80_percent_auto_binding_target(self):
        """Test 80% auto-binding target (8/10 variables)."""
        binder = VariableAutoBinder()
        
        variables = [
            "file_path", "module_name", "test_count", "coverage",
            "author", "timestamp", "phase", "status", "severity", "description"
        ]
        context = {
            "file_path": "app.py",
            "module": "core",
            "tests": 10,
            "coverage_pct": 85,
            "user": "dev1",
            "date": "2026-02-12",
            "phase_id": "P1",
            "state": "active",
            # Missing: severity, description
        }
        
        bound = binder.bind(variables, context)
        
        # Should bind at least 80% (8/10)
        assert len(bound) >= 8


# ============================================================================
# TEST: TemplateFusionEngine
# ============================================================================


class TestTemplateFusionEngine:
    """Test template fusion engine."""

    def test_fusion_engine_initialization(self):
        """Test fusion engine initializes registries."""
        engine = TemplateFusionEngine()
        
        assert engine.role_registry is not None
        assert engine.orchestrator_registry is not None

    def test_parse_structure_arrow_format(self):
        """Test parsing structure with arrows."""
        engine = TemplateFusionEngine()
        
        structure = "Analysis → Design → Implementation → Testing"
        sections = engine._parse_structure(structure)
        
        assert len(sections) == 4
        assert sections[0] == "Analysis"
        assert sections[3] == "Testing"

    def test_parse_structure_single_section(self):
        """Test parsing single-section structure."""
        engine = TemplateFusionEngine()
        
        structure = "Implementation"
        sections = engine._parse_structure(structure)
        
        assert len(sections) == 1
        assert sections[0] == "Implementation"


# ============================================================================
# TEST: UnifiedResponseEngine
# ============================================================================


class TestUnifiedResponseEngine:
    """Test unified response engine end-to-end."""

    def test_engine_initialization_default_config(self):
        """Test engine initializes with default config."""
        engine = UnifiedResponseEngine()
        
        assert engine.config is not None
        assert engine.role_mapper is not None
        assert engine.fusion_engine is not None
        assert engine.var_binder is not None

    def test_engine_initialization_custom_config(self):
        """Test engine initializes with custom config."""
        config = ResponseEngineConfig(feature_flag_enabled=True)
        engine = UnifiedResponseEngine(config)
        
        assert engine.config.feature_flag_enabled is True

    def test_intent_to_task_mapping(self):
        """Test intent to task conversion."""
        engine = UnifiedResponseEngine()
        
        assert engine._intent_to_task(IntentType.IMPLEMENT) == "implementation"
        assert engine._intent_to_task(IntentType.FIX) == "bugfix"
        assert engine._intent_to_task(IntentType.REFACTOR) == "refactor"
        assert engine._intent_to_task(IntentType.ANALYZE) == "analysis"

    def test_compose_with_feature_flag_disabled(self):
        """Test compose falls back when feature flag disabled."""
        config = ResponseEngineConfig(feature_flag_enabled=False)
        engine = UnifiedResponseEngine(config)
        
        result = engine.compose(
            intent=IntentType.IMPLEMENT,
            orchestrator_name="TDDOrchestrator",
            context={"file_path": "app.py"}
        )
        
        # Should use fallback
        assert "fallback" in result.lower() or "orchestrator" in result.lower()

    def test_fallback_compose_missing_template(self):
        """Test fallback compose with missing template."""
        engine = UnifiedResponseEngine()
        
        result = engine._fallback_compose(
            orchestrator_name="NonexistentOrchestrator",
            context={}
        )
        
        assert "ERROR" in result
        assert "NonexistentOrchestrator" in result


# ============================================================================
# TEST: Integration & Edge Cases
# ============================================================================


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""

    def test_end_to_end_implement_flow(self):
        """Test complete IMPLEMENT intent flow."""
        config = ResponseEngineConfig(
            feature_flag_enabled=False,  # Use fallback for now
            fallback_to_orchestrator=True
        )
        engine = UnifiedResponseEngine(config)
        
        result = engine.compose(
            intent=IntentType.IMPLEMENT,
            orchestrator_name="TDDOrchestrator",
            context={
                "file_path": "app.py",
                "test_count": 10,
                "coverage": 85
            }
        )
        
        assert result is not None
        assert len(result) > 0

    def test_multiple_intent_types(self):
        """Test engine handles multiple intent types."""
        engine = UnifiedResponseEngine()
        
        intents = [
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.ANALYZE,
            IntentType.PLAN
        ]
        
        for intent in intents:
            role = engine.role_mapper.get_role(intent)
            assert role in [
                Role.ENGINEER,
                Role.CTO,
                Role.PRODUCT_MANAGER
            ]

    def test_graceful_degradation_on_error(self):
        """Test graceful degradation when fusion fails."""
        config = ResponseEngineConfig(
            feature_flag_enabled=True,
            fallback_to_orchestrator=True
        )
        engine = UnifiedResponseEngine(config)
        
        # Should fall back gracefully even with feature flag enabled
        result = engine.compose(
            intent=IntentType.IMPLEMENT,
            orchestrator_name="TDDOrchestrator",
            context={}
        )
        
        assert result is not None


# ============================================================================
# TEST: Performance & Metrics
# ============================================================================


class TestPerformanceMetrics:
    """Test performance and metrics tracking."""

    def test_role_detection_performance(self):
        """Test role detection is fast (<1ms)."""
        import time
        
        mapper = IntentRoleMapper()
        
        start = time.perf_counter()
        for _ in range(1000):
            mapper.get_role(IntentType.IMPLEMENT)
        end = time.perf_counter()
        
        # Should be < 1ms per call
        avg_time = (end - start) / 1000
        assert avg_time < 0.001  # 1ms

    def test_variable_binding_coverage(self):
        """Test variable binding achieves 80%+ coverage."""
        binder = VariableAutoBinder()
        
        # Realistic scenario: 10 variables, comprehensive context
        variables = [
            "file_path", "module_name", "test_count", "coverage",
            "author", "timestamp", "phase", "status", "severity", "description"
        ]
        context = {
            "file_path": "app.py",
            "module": "core",
            "tests_passing": 20,
            "coverage": 90,
            "user": "dev",
            "date": "2026-02-12",
            "current_phase": "P1",
            "state": "active",
            "level": "info",
            # Missing: description (1/10)
        }
        
        bound = binder.bind(variables, context)
        coverage = len(bound) / len(variables)
        
        # Should achieve 80%+ (9/10 = 90%)
        assert coverage >= 0.8

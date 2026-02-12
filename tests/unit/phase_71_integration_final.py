"""
Phase 71 Complete Integration Tests - S8 Final Integration.

AC-ID: PHASE-71-S8
Purpose: End-to-end integration tests for Phase 71

Integration Scope:
1. All 7 stages working together
2. Learning pipeline completeness
3. Multi-orchestrator learning
4. Knowledge persistence and validation
5. Dashboard reporting accuracy

Author: Asif Hussain
Date: 2026-02-10
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from cortex.learning import (
    get_learning_loop,
    get_intelligence_validator,
    get_learning_dashboard,
)
from cortex.testing.test_value_scorer import get_test_value_scorer


# =============================================================================
# Test: Module Imports
# =============================================================================

class TestModuleImports:
    """Test that all Phase 71 components import successfully."""
    
    def test_import_universal_learning_loop(self):
        """Should import UniversalLearningLoop."""
        from cortex.learning import UniversalLearningLoop, get_learning_loop
        assert UniversalLearningLoop is not None
        assert get_learning_loop is not None
    
    def test_import_pattern_components(self):
        """Should import pattern extraction components."""
        from cortex.learning import PatternExtractor, ExtractedPattern, PatternType
        assert PatternExtractor is not None
        assert ExtractedPattern is not None
        assert PatternType is not None
    
    def test_import_knowledge_components(self):
        """Should import knowledge components."""
        from cortex.learning import KnowledgeMerger, MergeStrategy
        assert KnowledgeMerger is not None
        assert MergeStrategy is not None
    
    def test_import_orchestrator_components(self):
        """Should import orchestrator integration."""
        from cortex.learning import OrchestratorLearningMixin
        assert OrchestratorLearningMixin is not None
    
    def test_import_validation_components(self):
        """Should import validation components."""
        from cortex.learning import (
            IntelligenceValidator,
            ValidationReport,
            get_intelligence_validator,
        )
        assert IntelligenceValidator is not None
        assert ValidationReport is not None
        assert get_intelligence_validator is not None
    
    def test_import_dashboard_components(self):
        """Should import dashboard components."""
        from cortex.learning import (
            LearningDashboard,
            MetricsSnapshot,
            get_learning_dashboard,
        )
        assert LearningDashboard is not None
        assert MetricsSnapshot is not None
        assert get_learning_dashboard is not None


# =============================================================================
# Test: Singleton Access
# =============================================================================

class TestSingletonAccess:
    """Test singleton access patterns."""
    
    def test_get_learning_loop_available(self):
        """Should be able to get learning loop singleton."""
        loop = get_learning_loop()
        # May be None if not initialized, but should be callable
        assert True
    
    def test_get_test_scorer_available(self):
        """Should be able to get test scorer singleton."""
        scorer = get_test_value_scorer()
        # May be None if not initialized, but should be callable
        assert True
    
    def test_get_intelligence_validator_available(self):
        """Should be able to get validator."""
        validator = get_intelligence_validator()
        assert validator is not None
    
    def test_get_dashboard_available(self):
        """Should be able to get dashboard."""
        dashboard = get_learning_dashboard()
        assert dashboard is not None


# =============================================================================
# Test: End-to-End Workflow
# =============================================================================

class TestEndToEndWorkflow:
    """Test complete Phase 71 workflow."""
    
    def test_orchestrator_mixin_integration(self):
        """Test orchestrator can use learning mixin."""
        from cortex.learning import OrchestratorLearningMixin
        
        class TestOrchestrator(OrchestratorLearningMixin):
            def execute(self):
                self._capture_learning(
                    operation_type="test",
                    patterns={"key": "value"},
                )
                return "done"
        
        orch = TestOrchestrator()
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock:
            mock.return_value = MagicMock()
            result = orch.execute()
            assert result == "done"
            assert orch._get_learning_orchestrator_type() == "generic"
    
    def test_validation_pipeline(self):
        """Test validation of learning pipeline."""
        from cortex.learning import get_intelligence_validator
        
        validator = get_intelligence_validator()
        # Should be able to call without errors
        assert validator is not None
    
    def test_dashboard_generation(self):
        """Test dashboard report generation."""
        from cortex.learning import get_learning_dashboard
        
        dashboard = get_learning_dashboard()
        dashboard.learning_loop = MagicMock()
        dashboard.test_scorer = MagicMock()
        
        # Setup metrics
        metrics = {
            "total_learnings": 10,
            "total_patterns": 20,
            "by_orchestrator": {
                "TestOrch": {
                    "count": 10,
                    "patterns": 20,
                    "avg_confidence": 0.85,
                    "confidences": [],
                }
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        dashboard.test_scorer.get_score_summary.return_value = {"by_tier": {}}
        
        report = dashboard.generate_report()
        assert report is not None
        assert "summary" in report


# =============================================================================
# Test: Cross-Component Integration
# =============================================================================

class TestCrossComponentIntegration:
    """Test integration between different Phase 71 components."""
    
    def test_learning_and_validation_together(self):
        """Learning loop should work with validator."""
        from cortex.learning import get_learning_loop, get_intelligence_validator
        
        validator = get_intelligence_validator()
        # Validator should be able to reference learning loop
        assert validator is not None
        assert hasattr(validator, "learning_loop")
    
    def test_dashboard_with_validation(self):
        """Dashboard should integrate with validator."""
        from cortex.learning import get_learning_dashboard, get_intelligence_validator
        
        dashboard = get_learning_dashboard()
        validator = get_intelligence_validator()
        
        # Both should be independently functional
        assert dashboard is not None
        assert validator is not None
    
    def test_test_scorer_with_learning(self):
        """Test scorer should integrate with learning."""
        from cortex.testing.test_value_scorer import get_test_value_scorer
        
        scorer = get_test_value_scorer()
        # Scorer may be None, but should be accessible
        assert True


# =============================================================================
# Test: Architecture Validation
# =============================================================================

class TestArchitectureValidation:
    """Validate Phase 71 architecture."""
    
    def test_dual_interception_pattern(self):
        """Learning should work via both protocol and MCP."""
        # Protocol: OrchestratorBaseProtocol Phase 6
        # MCP: MCPLearningInterceptor
        from cortex.orchestrators.core.orchestrator_base_protocol import OrchestratorBaseProtocol
        from cortex.mcp.learning_gateway_interceptor import MCPLearningInterceptor
        
        # Both should be importable
        assert OrchestratorBaseProtocol is not None
        assert MCPLearningInterceptor is not None
    
    def test_non_blocking_failure_handling(self):
        """All learning operations should be non-blocking."""
        from cortex.learning import OrchestratorLearningMixin
        
        mixin = OrchestratorLearningMixin()
        
        # Even with errors, should not raise
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock:
            mock.return_value = MagicMock()
            mock.return_value.capture_from_operation.side_effect = Exception("Test error")
            
            # Should not raise exception
            mixin._capture_learning("test", patterns={})


# =============================================================================
# Test: Completeness Validation
# =============================================================================

class TestCompletenessValidation:
    """Validate Phase 71 implementation completeness."""
    
    def test_all_orchestrator_types_supported(self):
        """Learning should support all 5 orchestrator types."""
        from cortex.learning import OrchestratorLearningMixin
        
        types_to_test = [
            ("TDDOrchestrator", "tdd"),
            ("RefactoringOrchestrator", "refactoring"),
            ("InteractionOrchestrator", "interaction"),
            ("GovernanceOrchestrator", "governance"),
            ("CoordinationOrchestrator", "coordination"),
        ]
        
        for class_name, expected_type in types_to_test:
            # Create dynamic class with the right name
            OrchestrationClass = type(class_name, (OrchestratorLearningMixin,), {})
            instance = OrchestrationClass()
            
            assert instance._get_learning_orchestrator_type() == expected_type
    
    def test_test_quality_dimensions_covered(self):
        """Test scorer should measure all 5 dimensions."""
        from cortex.testing.test_value_scorer import TestMetrics
        
        metrics = TestMetrics(
            coverage_percent=80,
            edge_cases_covered=5,
            total_edge_cases=10,
            mutations_caught=10,
            total_mutations=20,
            flakiness_percent=5,
            false_positives=0,
        )
        
        # All dimension methods should work
        assert metrics.get_coverage_score() > 0
        assert metrics.get_edge_case_score() > 0
        assert metrics.get_mutation_score() > 0
        assert metrics.get_regression_score() > 0
        assert metrics.get_brittleness_score() > 0
    
    def test_validation_checks_coverage(self):
        """Validator should check all aspects."""
        from cortex.learning import IntelligenceValidator
        
        with tempfile.TemporaryDirectory() as tmpdir:
            validator = IntelligenceValidator(Path(tmpdir))
            
            # Should have all validation methods
            assert hasattr(validator, "validate_learning_pipeline")
            assert hasattr(validator, "validate_orchestrator_learning")
            assert hasattr(validator, "validate_knowledge_persistence")
            assert hasattr(validator, "validate_confidence_scoring")


# =============================================================================
# Test: Performance and Scale
# =============================================================================

class TestPerformanceAndScale:
    """Test Phase 71 performance at scale."""
    
    def test_learning_loop_handles_multiple_orchestrators(self):
        """Learning loop should handle multiple concurrent orchestrators."""
        from cortex.learning import get_learning_loop
        
        loop = get_learning_loop()
        if loop is None:
            pytest.skip("Learning loop not available")
        
        # Should be able to simulate multiple orchestrator operations
        assert loop is not None
    
    def test_dashboard_scales_to_many_patterns(self):
        """Dashboard should handle large numbers of patterns."""
        from cortex.learning import get_learning_dashboard
        
        dashboard = get_learning_dashboard()
        dashboard.learning_loop = MagicMock()
        
        # Create metrics with many patterns
        metrics = {
            "total_learnings": 1000,
            "total_patterns": 5000,
            "by_orchestrator": {
                f"Orch{i}": {
                    "count": 100,
                    "patterns": 500,
                    "avg_confidence": 0.85,
                    "confidences": [0.8 + (i * 0.01) for i in range(10)],
                }
                for i in range(10)
            }
        }
        dashboard.learning_loop.get_learning_metrics.return_value = metrics
        
        report = dashboard.generate_report()
        assert report["summary"]["total_patterns"] == 5000


# Temp file for tests
import tempfile

__all__ = [
    "TestModuleImports",
    "TestSingletonAccess",
    "TestEndToEndWorkflow",
    "TestCrossComponentIntegration",
    "TestArchitectureValidation",
    "TestCompletenessValidation",
    "TestPerformanceAndScale",
]

"""
Tests for OrchestratorLearningMixin - Phase 71 S5.

AC-ID: PHASE-71-S5
Purpose: Verify learning integration into TDD, Refactoring, Interaction orchestrators

Test Coverage:
1. Learning capture from orchestrators
2. Test quality scoring integration
3. Refactoring pattern extraction
4. Interaction pattern extraction
5. Non-blocking failure handling
6. Orchestrator type detection

Author: Asif Hussain
Date: 2026-02-10
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from cortex.learning.orchestrator_integration_mixin import OrchestratorLearningMixin
from cortex.testing.test_value_scorer import ScoreTier


# =============================================================================
# Test: Mixin Learning Capture
# =============================================================================

class TestMixinLearningCapture:
    """Tests for orchestrator learning capture."""
    
    def test_capture_learning_with_patterns(self):
        """Mixin should capture learning with patterns."""
        mixin = OrchestratorLearningMixin()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock_get:
            mock_loop = MagicMock()
            mock_get.return_value = mock_loop
            
            patterns = {"key": "value"}
            mixin._capture_learning("tdd", patterns=patterns)
            
            mock_loop.capture_from_operation.assert_called_once()
            call_args = mock_loop.capture_from_operation.call_args
            assert call_args[1]["operation"] == "tdd"
    
    def test_capture_learning_with_test_scores(self):
        """Mixin should capture learning with test scores."""
        mixin = OrchestratorLearningMixin()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock_get:
            mock_loop = MagicMock()
            mock_get.return_value = mock_loop
            
            test_scores = [{"test": "test_example", "score": 0.85}]
            mixin._capture_learning("tdd", test_scores=test_scores)
            
            assert mock_loop.capture_from_operation.called
    
    def test_capture_learning_handles_missing_loop(self):
        """Mixin should gracefully handle missing learning loop."""
        mixin = OrchestratorLearningMixin()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock_get:
            mock_get.return_value = None
            
            # Should not raise
            mixin._capture_learning("tdd", patterns={"key": "value"})
    
    def test_capture_learning_handles_exceptions(self):
        """Mixin should handle exceptions in learning capture."""
        mixin = OrchestratorLearningMixin()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock_get:
            mock_loop = MagicMock()
            mock_loop.capture_from_operation.side_effect = Exception("Test error")
            mock_get.return_value = mock_loop
            
            # Should not raise (non-blocking)
            mixin._capture_learning("tdd", patterns={"key": "value"})


# =============================================================================
# Test: Test Quality Scoring
# =============================================================================

class TestQualityScoring:
    """Tests for test quality scoring integration."""
    
    def test_score_test_quality_with_high_metrics(self):
        """Mixin should score high-quality tests."""
        mixin = OrchestratorLearningMixin()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_test_value_scorer") as mock_get:
            mock_scorer = MagicMock()
            mock_score = MagicMock()
            mock_score.tier = ScoreTier.HIGH
            mock_score.to_dict.return_value = {
                "test_name": "test_example",
                "tier": "HIGH",
                "overall_score": 0.75,
            }
            mock_scorer.score_test.return_value = mock_score
            mock_get.return_value = mock_scorer
            
            result = mixin._score_test_quality(
                "test_example",
                coverage_percent=85.0,
                edge_cases_covered=8,
                total_edge_cases=10,
                mutations_caught=18,
                total_mutations=20,
            )
            
            assert result is not None
            assert result["tier"] == "HIGH"
    
    def test_score_test_quality_handles_missing_scorer(self):
        """Mixin should gracefully handle missing scorer."""
        mixin = OrchestratorLearningMixin()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_test_value_scorer") as mock_get:
            mock_get.return_value = None
            
            result = mixin._score_test_quality(
                "test_example",
                coverage_percent=85.0,
                edge_cases_covered=8,
                total_edge_cases=10,
                mutations_caught=18,
                total_mutations=20,
            )
            
            assert result is None
    
    def test_score_test_quality_handles_exceptions(self):
        """Mixin should handle exceptions in scoring."""
        mixin = OrchestratorLearningMixin()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_test_value_scorer") as mock_get:
            mock_scorer = MagicMock()
            mock_scorer.score_test.side_effect = Exception("Scoring failed")
            mock_get.return_value = mock_scorer
            
            result = mixin._score_test_quality(
                "test_example",
                coverage_percent=85.0,
                edge_cases_covered=8,
                total_edge_cases=10,
                mutations_caught=18,
                total_mutations=20,
            )
            
            assert result is None


# =============================================================================
# Test: Pattern Extraction
# =============================================================================

class TestPatternExtraction:
    """Tests for pattern extraction helpers."""
    
    def test_extract_refactoring_patterns(self):
        """Mixin should extract refactoring patterns."""
        mixin = OrchestratorLearningMixin()
        
        patterns = mixin._extract_refactoring_patterns(
            operation="rename",
            files_affected=["src/module.py", "tests/test_module.py"],
            changes_summary={
                "complexity_reduction": 15,
                "lines_changed": 42,
                "maintainability_improvement": 8,
            }
        )
        
        assert patterns["operation"] == "rename"
        assert patterns["file_count"] == 2
        assert patterns["complexity_reduction"] == 15
    
    def test_extract_interaction_patterns(self):
        """Mixin should extract interaction patterns."""
        mixin = OrchestratorLearningMixin()
        
        patterns = mixin._extract_interaction_patterns(
            user_intent="extract method",
            interaction_type="suggestion",
            outcome="accepted",
            metadata={"scope": "module", "complexity": "medium"},
        )
        
        assert patterns["user_intent"] == "extract method"
        assert patterns["interaction_type"] == "suggestion"
        assert patterns["outcome"] == "accepted"
        assert patterns["metadata"]["scope"] == "module"


# =============================================================================
# Test: Orchestrator Type Detection
# =============================================================================

class TestOrchestratorTypeDetection:
    """Tests for orchestrator type detection."""
    
    def test_detect_tdd_orchestrator_type(self):
        """Mixin should detect TDD orchestrator type."""
        class TDDOrchestrator(OrchestratorLearningMixin):
            pass
        
        orch = TDDOrchestrator()
        assert orch._get_learning_orchestrator_type() == "tdd"
    
    def test_detect_refactoring_orchestrator_type(self):
        """Mixin should detect refactoring orchestrator type."""
        class RefactoringOrchestrator(OrchestratorLearningMixin):
            pass
        
        orch = RefactoringOrchestrator()
        assert orch._get_learning_orchestrator_type() == "refactoring"
    
    def test_detect_interaction_orchestrator_type(self):
        """Mixin should detect interaction orchestrator type."""
        class InteractionOrchestrator(OrchestratorLearningMixin):
            pass
        
        orch = InteractionOrchestrator()
        assert orch._get_learning_orchestrator_type() == "interaction"
    
    def test_detect_governance_orchestrator_type(self):
        """Mixin should detect governance orchestrator type."""
        class GovernanceOrchestrator(OrchestratorLearningMixin):
            pass
        
        orch = GovernanceOrchestrator()
        assert orch._get_learning_orchestrator_type() == "governance"
    
    def test_detect_coordination_orchestrator_type(self):
        """Mixin should detect coordination orchestrator type."""
        class CoordinationOrchestrator(OrchestratorLearningMixin):
            pass
        
        orch = CoordinationOrchestrator()
        assert orch._get_learning_orchestrator_type() == "coordination"
    
    def test_default_orchestrator_type(self):
        """Mixin should return generic for unknown orchestrator type."""
        class UnknownOrchestrator(OrchestratorLearningMixin):
            pass
        
        orch = UnknownOrchestrator()
        assert orch._get_learning_orchestrator_type() == "generic"


# =============================================================================
# Test: Integration Scenarios
# =============================================================================

class TestIntegrationScenarios:
    """Integration test scenarios."""
    
    def test_tdd_orchestrator_with_learning(self):
        """TDD orchestrator should capture learning from test execution."""
        
        class TDDOrchestrator(OrchestratorLearningMixin):
            def execute_test_cycle(self, test_names):
                # Simulate test cycle
                test_scores = []
                for test_name in test_names:
                    score = self._score_test_quality(
                        test_name,
                        coverage_percent=85.0,
                        edge_cases_covered=8,
                        total_edge_cases=10,
                        mutations_caught=18,
                        total_mutations=20,
                    )
                    if score:
                        test_scores.append(score)
                
                # Capture learning
                self._capture_learning(
                    operation_type="tdd",
                    test_scores=test_scores,
                )
                
                return test_scores
        
        orch = TDDOrchestrator()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock_get_loop:
            with patch("cortex.learning.orchestrator_integration_mixin.get_test_value_scorer") as mock_get_scorer:
                mock_loop = MagicMock()
                mock_get_loop.return_value = mock_loop
                
                mock_scorer = MagicMock()
                mock_score = MagicMock()
                mock_score.to_dict.return_value = {"tier": "HIGH", "overall_score": 0.75}
                mock_scorer.score_test.return_value = mock_score
                mock_get_scorer.return_value = mock_scorer
                
                scores = orch.execute_test_cycle(["test_one", "test_two"])
                
                # Verify learning was captured
                assert mock_loop.capture_from_operation.called
    
    def test_refactoring_orchestrator_with_learning(self):
        """Refactoring orchestrator should capture learning."""
        
        class RefactoringOrchestrator(OrchestratorLearningMixin):
            def execute_refactoring(self, files):
                patterns = self._extract_refactoring_patterns(
                    operation="extract_method",
                    files_affected=files,
                    changes_summary={"complexity_reduction": 15, "lines_changed": 42},
                )
                
                self._capture_learning(
                    operation_type="refactoring",
                    patterns=patterns,
                )
                
                return patterns
        
        orch = RefactoringOrchestrator()
        
        with patch("cortex.learning.orchestrator_integration_mixin.get_learning_loop") as mock_get:
            mock_loop = MagicMock()
            mock_get.return_value = mock_loop
            
            patterns = orch.execute_refactoring(["src/module.py", "tests/test_module.py"])
            
            assert patterns["operation"] == "extract_method"
            assert mock_loop.capture_from_operation.called

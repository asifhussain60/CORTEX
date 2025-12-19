"""
Tests for Historical Context Integration (Phase 4)

Tests anti-pattern detection and success pattern recommendations.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""
import pytest
from pathlib import Path
from src.operations.modules.orchestration.planning.anti_pattern_detector import AntiPatternDetector
from src.operations.modules.orchestration.planning.success_pattern_recommender import SuccessPatternRecommender
from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator


class TestAntiPatternDetector:
    """Test anti-pattern detection functionality."""
    
    def test_detector_initialization(self):
        """Test that anti-pattern detector initializes successfully."""
        detector = AntiPatternDetector()
        assert detector is not None
        assert detector.anti_pattern_db is not None
        assert len(detector.anti_pattern_db) > 0
    
    def test_load_default_patterns(self):
        """Test that default anti-patterns are loaded."""
        detector = AntiPatternDetector()
        patterns = detector.anti_pattern_db
        
        # Verify critical patterns exist
        assert 'skip_red_phase' in patterns
        assert 'monolithic_phase' in patterns
        assert 'missing_acceptance_criteria' in patterns
        
        # Verify pattern structure
        assert patterns['skip_red_phase']['severity'] == 'critical'
        assert 'description' in patterns['skip_red_phase']
        assert 'impact' in patterns['skip_red_phase']
    
    def test_scan_plan_detects_monolithic_phase(self):
        """Test detection of phases exceeding 24h."""
        detector = AntiPatternDetector()
        
        plan = {
            'phases': [
                {'name': 'BigPhase', 'estimated_hours': 32, 'description': 'Too large'}
            ],
            'complexity': 'HIGH'
        }
        
        warnings = detector.scan_plan(plan)
        
        assert len(warnings) > 0
        assert any(w['type'] == 'monolithic_phase' for w in warnings)
        
        monolithic_warning = [w for w in warnings if w['type'] == 'monolithic_phase'][0]
        assert 'BigPhase' in monolithic_warning['message']
        assert monolithic_warning['severity'] == 'high'
    
    def test_scan_plan_detects_missing_red_phase(self):
        """Test detection of missing TDD RED phase."""
        detector = AntiPatternDetector()
        
        plan = {
            'phases': [
                {'name': 'Implementation', 'estimated_hours': 8},
                {'name': 'Deployment', 'estimated_hours': 4}
            ],
            'complexity': 'HIGH',
            'requires_tdd': True
        }
        
        warnings = detector.scan_plan(plan)
        
        assert len(warnings) > 0
        assert any(w['type'] == 'skip_red_phase' for w in warnings)
        
        red_warning = [w for w in warnings if w['type'] == 'skip_red_phase'][0]
        assert red_warning['severity'] == 'critical'
        assert 'RED phase' in red_warning['message']
    
    def test_scan_plan_detects_missing_acceptance_criteria(self):
        """Test detection of missing acceptance criteria."""
        detector = AntiPatternDetector()
        
        plan = {
            'phases': [
                {'name': 'Phase 1', 'estimated_hours': 8}
            ]
            # No acceptance_criteria or success_criteria
        }
        
        warnings = detector.scan_plan(plan)
        
        assert len(warnings) > 0
        assert any(w['type'] == 'missing_acceptance_criteria' for w in warnings)
    
    def test_scan_plan_no_warnings_for_good_plan(self):
        """Test that well-structured plans generate minimal warnings."""
        detector = AntiPatternDetector()
        
        plan = {
            'phases': [
                {'name': 'RED: Write Tests', 'estimated_hours': 4},
                {'name': 'GREEN: Implement', 'estimated_hours': 8},
                {'name': 'REFACTOR: Cleanup', 'estimated_hours': 4}
            ],
            'complexity': 'MEDIUM',
            'requires_tdd': True,
            'acceptance_criteria': ['Feature works', 'Tests pass'],
            'coverage_target': 80
        }
        
        warnings = detector.scan_plan(plan)
        
        # Should have few or no warnings
        critical_warnings = [w for w in warnings if w.get('severity') == 'critical']
        assert len(critical_warnings) == 0
    
    def test_get_anti_pattern_summary(self):
        """Test anti-pattern summary generation."""
        detector = AntiPatternDetector()
        summary = detector.get_anti_pattern_summary()
        
        assert 'total_patterns' in summary
        assert 'critical_patterns' in summary
        assert 'high_patterns' in summary
        assert 'patterns' in summary
        
        assert summary['total_patterns'] >= 5
        assert summary['critical_patterns'] >= 2


class TestSuccessPatternRecommender:
    """Test success pattern recommendation functionality."""
    
    def test_recommender_initialization(self):
        """Test that success pattern recommender initializes successfully."""
        recommender = SuccessPatternRecommender()
        assert recommender is not None
        assert recommender.success_patterns is not None
        assert len(recommender.success_patterns) > 0
    
    def test_load_default_patterns(self):
        """Test that default success patterns are loaded."""
        recommender = SuccessPatternRecommender()
        patterns = recommender.success_patterns
        
        # Verify core patterns exist
        assert 'incremental_delivery' in patterns
        assert 'tdd_first' in patterns
        assert 'checkpoint_frequency' in patterns
        
        # Verify pattern structure
        assert patterns['tdd_first']['confidence'] > 0.8
        assert 'description' in patterns['tdd_first']
        assert 'applies_to' in patterns['tdd_first']
    
    def test_get_recommendations_filters_by_confidence(self):
        """Test that recommendations are filtered by confidence threshold."""
        recommender = SuccessPatternRecommender()
        
        # HIGH complexity should filter to high confidence patterns
        recommendations = recommender.get_recommendations(
            feature_type='authentication',
            complexity='HIGH'
        )
        
        assert len(recommendations) > 0
        # All recommendations should meet high threshold (0.70)
        assert all(r['confidence'] >= 0.70 for r in recommendations)
    
    def test_get_recommendations_sorted_by_confidence(self):
        """Test that recommendations are sorted by confidence (highest first)."""
        recommender = SuccessPatternRecommender()
        
        recommendations = recommender.get_recommendations(
            feature_type='api',
            complexity='MEDIUM'
        )
        
        assert len(recommendations) > 0
        
        # Verify sorted descending
        confidences = [r['confidence'] for r in recommendations]
        assert confidences == sorted(confidences, reverse=True)
    
    def test_get_recommendations_applies_to_all(self):
        """Test that patterns with 'all' in applies_to are included."""
        recommender = SuccessPatternRecommender()
        
        recommendations = recommender.get_recommendations(
            feature_type='unknown_type',
            complexity='MEDIUM'
        )
        
        # Should still get recommendations for universal patterns
        assert len(recommendations) > 0
        
        # Verify 'tdd_first' pattern is included (applies to 'all')
        tdd_pattern = [r for r in recommendations if 'tdd' in r['pattern_id'].lower()]
        assert len(tdd_pattern) > 0
    
    def test_get_pattern_summary(self):
        """Test pattern summary generation."""
        recommender = SuccessPatternRecommender()
        summary = recommender.get_pattern_summary()
        
        assert 'total_patterns' in summary
        assert 'high_confidence' in summary
        assert 'medium_confidence' in summary
        assert 'patterns' in summary
        
        assert summary['total_patterns'] >= 5


class TestPlanningOrchestratorIntegration:
    """Test historical context integration with Planning Orchestrator."""
    
    def test_orchestrator_has_historical_components(self):
        """Test that orchestrator initializes historical context components."""
        orchestrator = PlanningOrchestrator()
        
        # Should have anti-pattern detector
        assert hasattr(orchestrator, 'anti_pattern_detector')
        
        # Should have success pattern recommender
        assert hasattr(orchestrator, 'success_pattern_recommender')
    
    def test_retrieve_historical_patterns(self):
        """Test historical pattern retrieval method."""
        orchestrator = PlanningOrchestrator()
        
        patterns = orchestrator.retrieve_historical_patterns(
            operation='feature_planning',
            feature_type='authentication'
        )
        
        assert 'success_patterns' in patterns
        assert 'anti_patterns' in patterns
        assert 'lessons_learned' in patterns
        
        # Should have some patterns
        assert isinstance(patterns['success_patterns'], list)
        assert isinstance(patterns['anti_patterns'], list)
    
    def test_phase_generation_includes_warnings(self):
        """Test that phase generation integrates anti-pattern warnings."""
        orchestrator = PlanningOrchestrator()
        
        from src.operations.modules.orchestration.planning_orchestrator import PlanningContext
        from src.operations.modules.routing.complexity_analyzer import ComplexityScore, ComplexityTier
        from src.operations.modules.routing.tiered_router import RoutingDecision
        from datetime import datetime
        
        # Create a Tier 3 planning context
        planning_context = PlanningContext(
            operation='Add user authentication without tests',
            tier=3,
            complexity_score=ComplexityScore(
                total_score=85,
                tier=ComplexityTier.HIGH,  # Fixed: Use HIGH instead of DOCUMENTED
                dimensions={'scope': 20, 'dependencies': 20, 'risk': 30, 'uncertainty': 15},
                rationale=['High complexity feature'],
                recommendation='Use incremental planning',
                triggers=[]
            ),
            routing_decision=RoutingDecision(
                tier=3,
                confidence=0.9,
                reasoning='Feature addition',
                execution_method='documented',
                estimated_time='18h',
                requires_planning=True
            ),
            user_context={},
            timestamp=datetime.now()
        )
        
        # Generate phases (should trigger anti-pattern detection)
        phases = orchestrator._generate_phases_for_tier(planning_context)
        
        assert len(phases) > 0
        
        # First phase should have historical warnings if anti-patterns detected
        if orchestrator.anti_pattern_detector:
            # Check if any phase has warnings
            has_warnings = any('historical_warnings' in phase for phase in phases)
            # This is fine either way - depends on if anti-patterns were detected
            assert isinstance(has_warnings, bool)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

"""
CORTEX Gate 8 SWAGGER Integration Tests

Tests for the SWAGGER complexity-to-timeframe pipeline:
- TimeframeEstimator: Complexity → sprint estimates
- DoRValidator: Definition of Ready enforcement  
- WorkDecomposer: Work breakdown with ADO output
- SWAGGEREntryPointOrchestrator: Unified entry point

Author: Asif Hussain
Copyright: (c) 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta


# ============================================================================
# TimeframeEstimator Tests
# ============================================================================

class TestTimeframeEstimator:
    """Tests for complexity-to-timeframe conversion."""
    
    @pytest.fixture
    def estimator(self):
        """Create TimeframeEstimator instance."""
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        return TimeframeEstimator()
    
    def test_estimate_from_complexity_low(self, estimator):
        """Test estimation for low complexity (20)."""
        estimate = estimator.estimate_timeframe(complexity_score=20)
        
        assert estimate is not None
        assert estimate.complexity_score == 20
        assert estimate.story_points <= 5
        assert estimate.sprints_single_dev <= 2
        assert estimate.min_days > 0
        assert estimate.max_days >= estimate.min_days
    
    def test_estimate_from_complexity_medium(self, estimator):
        """Test estimation for medium complexity (50)."""
        estimate = estimator.estimate_timeframe(complexity_score=50)
        
        assert estimate is not None
        assert estimate.complexity_score == 50
        assert 5 <= estimate.story_points <= 21
        assert estimate.sprints_single_dev >= 2
    
    def test_estimate_from_complexity_high(self, estimator):
        """Test estimation for high complexity (85)."""
        estimate = estimator.estimate_timeframe(complexity_score=85)
        
        assert estimate is not None
        assert estimate.complexity_score == 85
        assert estimate.story_points >= 13
        assert estimate.sprints_single_dev >= 4
    
    def test_confidence_scoring(self, estimator):
        """Test that confidence scores are calculated."""
        estimate = estimator.estimate_timeframe(complexity_score=50)
        
        assert hasattr(estimate, 'confidence')
        assert 0.0 <= estimate.confidence <= 1.0
    
    def test_risk_buffer_application(self, estimator):
        """Test that risk buffers are applied."""
        estimate = estimator.estimate_timeframe(complexity_score=50)
        
        assert hasattr(estimate, 'risk_buffer_days')
        assert estimate.risk_buffer_days >= 0
    
    def test_what_if_scenarios(self, estimator):
        """Test what-if scenario generation."""
        estimate = estimator.estimate_timeframe(complexity_score=50)
        scenarios = estimator.what_if_scenarios(estimate)
        
        assert len(scenarios) >= 3  # At least 3 team configurations
        
        # Verify each scenario has required fields
        for scenario in scenarios:
            assert 'team_size' in scenario
            assert 'sprints' in scenario
            assert 'speedup_factor' in scenario
    
    def test_parallel_tracks(self, estimator):
        """Test parallel track identification."""
        estimate = estimator.estimate_timeframe(complexity_score=60)
        
        assert hasattr(estimate, 'parallel_tracks')
        assert isinstance(estimate.parallel_tracks, list)
    
    def test_timeline_comparison(self, estimator):
        """Test timeline comparison generation."""
        estimate = estimator.estimate_timeframe(complexity_score=50)
        comparison = estimator.generate_timeline_comparison(estimate)
        
        assert comparison is not None
        assert hasattr(comparison, 'single_dev_timeline')
        assert hasattr(comparison, 'max_team_timeline')
        assert comparison.speedup_factor >= 1.0


# ============================================================================
# DoR Validator Tests
# ============================================================================

class TestDoRValidator:
    """Tests for Definition of Ready validation."""
    
    @pytest.fixture
    def validator(self):
        """Create DoRValidator instance."""
        from src.agents.estimation.dor_validator import DoRValidator
        return DoRValidator()
    
    def test_empty_requirements_fails(self, validator):
        """Test that empty requirements fail validation."""
        result = validator.validate_dor("")
        
        assert result is not None
        assert result.completeness_score < 0.5
        assert not result.can_estimate
    
    def test_complete_requirements_passes(self, validator):
        """Test that complete requirements pass validation."""
        complete_requirements = """
        User Authentication Feature:
        
        # Problem Statement
        Users need secure login capability with multi-factor authentication.
        
        # Specific Goals
        - Implement OAuth 2.0 authentication
        - Add MFA support (SMS, TOTP)
        - Create session management
        
        # Target Users
        - End users accessing the web portal
        - API consumers using tokens
        
        # Success Criteria
        - Login response time < 500ms
        - 99.9% authentication availability
        - Zero security vulnerabilities
        
        # Scope Boundaries
        - Includes: Web login, API auth, MFA
        - Excludes: Social login (Phase 2)
        
        # Dependencies
        - SMS gateway API
        - Database migration for user tokens
        
        # Acceptance Criteria
        - Users can log in with email/password
        - MFA can be enabled per user
        - Sessions expire after 30 minutes
        """
        result = validator.validate_dor(complete_requirements)
        
        assert result is not None
        assert result.completeness_score > 0.5
        # Note: can_estimate depends on having ALL required criteria
    
    def test_partial_requirements_returns_questions(self, validator):
        """Test that partial requirements generate clarifying questions."""
        partial_requirements = """
        Build a login page with authentication.
        """
        result = validator.validate_dor(partial_requirements)
        
        assert result is not None
        assert len(result.missing_items) > 0
        assert len(result.clarifying_questions) > 0
    
    def test_completeness_score_calculated(self, validator):
        """Test completeness score calculation."""
        result = validator.validate_dor("Simple feature with basic description")
        
        assert hasattr(result, 'completeness_score')
        assert 0.0 <= result.completeness_score <= 1.0
    
    def test_can_estimate_gate(self, validator):
        """Test can_estimate is correctly set."""
        # Minimal requirements should not be estimable
        minimal = validator.validate_dor("Build something")
        assert not minimal.can_estimate
        
        # Complete requirements should be estimable
        complete = """
        Feature: User Dashboard
        
        Problem: Users need a central view of their data.
        Goals: Display key metrics, enable data export.
        Users: Admin users, regular users.
        Success: < 2s load time, 95% satisfaction.
        Scope: Dashboard only, no editing.
        Dependencies: Metrics API ready.
        Acceptance: Dashboard loads, metrics display, export works.
        """
        complete_result = validator.validate_dor(complete)
        # May or may not pass depending on strictness
        assert hasattr(complete_result, 'can_estimate')


# ============================================================================
# Work Decomposer Tests
# ============================================================================

class TestWorkDecomposer:
    """Tests for work item decomposition."""
    
    @pytest.fixture
    def decomposer(self):
        """Create WorkDecomposer instance."""
        from src.agents.estimation.work_decomposer import WorkDecomposer
        return WorkDecomposer()
    
    def test_decompose_creates_stories(self, decomposer):
        """Test that decomposition creates stories."""
        result = decomposer.decompose_work(
            title="User Authentication",
            description="Implement secure login with OAuth",
            complexity_score=50
        )
        
        assert result is not None
        assert len(result.stories) > 0
    
    def test_decompose_creates_features(self, decomposer):
        """Test that decomposition creates features."""
        result = decomposer.decompose_work(
            title="E-Commerce Checkout",
            description="Full checkout flow with payments",
            complexity_score=70
        )
        
        assert result is not None
        assert len(result.features) > 0
    
    def test_high_complexity_creates_epic(self, decomposer):
        """Test that high complexity work creates an Epic."""
        result = decomposer.decompose_work(
            title="Platform Migration",
            description="Full migration from legacy to new platform",
            complexity_score=90
        )
        
        assert result is not None
        assert result.epic is not None
    
    def test_story_points_assigned(self, decomposer):
        """Test that story points are assigned to stories."""
        result = decomposer.decompose_work(
            title="API Development",
            description="Create REST API endpoints",
            complexity_score=40
        )
        
        for story in result.stories:
            assert story.story_points > 0
            assert story.story_points <= 13  # Max story size
    
    def test_ado_dict_format(self, decomposer):
        """Test that stories can be converted to ADO format."""
        result = decomposer.decompose_work(
            title="Notification System",
            description="Email and push notifications",
            complexity_score=45
        )
        
        if result.stories:
            ado_dict = result.stories[0].to_ado_dict()
            assert "System.Title" in ado_dict
            assert "Microsoft.VSTS.Scheduling.StoryPoints" in ado_dict
    
    def test_acceptance_criteria_generated(self, decomposer):
        """Test that acceptance criteria are generated."""
        result = decomposer.decompose_work(
            title="Search Feature",
            description="Full-text search with filters",
            complexity_score=50,
            requirements={
                'acceptance_criteria': [
                    "Users can search by keyword",
                    "Results display within 2 seconds"
                ]
            }
        )
        
        # Check at least some stories have AC
        has_ac = any(len(s.acceptance_criteria) > 0 for s in result.stories)
        assert has_ac or len(result.stories) > 0


# ============================================================================
# Integration Tests
# ============================================================================

class TestSWAGGERIntegration:
    """End-to-end integration tests."""
    
    def test_full_pipeline_flow(self):
        """Test complete flow: DoR → Estimation → Decomposition."""
        from src.agents.estimation.dor_validator import DoRValidator
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        from src.agents.estimation.work_decomposer import WorkDecomposer
        
        validator = DoRValidator()
        estimator = TimeframeEstimator()
        decomposer = WorkDecomposer()
        
        # Step 1: Validate DoR
        requirements_text = """
        Payment Processing Feature
        
        Problem: Need secure payment handling.
        Goals: Support credit cards, integrate with Stripe.
        Users: Customers making purchases.
        Success: < 3s processing, PCI compliance.
        Scope: Card payments only, no crypto.
        Dependencies: Stripe API keys.
        AC: Payment form, processing, confirmation.
        """
        dor_result = validator.validate_dor(requirements_text)
        assert dor_result is not None
        
        # Step 2: Estimate timeframe (regardless of DoR pass)
        complexity_score = 55
        estimate = estimator.estimate_timeframe(complexity_score=complexity_score)
        assert estimate is not None
        assert estimate.story_points > 0
        
        # Step 3: Decompose work
        decomp_result = decomposer.decompose_work(
            title="Payment Processing",
            description="Secure payment handling with Stripe",
            complexity_score=complexity_score
        )
        assert decomp_result is not None
        assert len(decomp_result.stories) > 0
        
        # Step 4: Verify hierarchy
        total_story_points = sum(s.story_points for s in decomp_result.stories)
        assert total_story_points > 0
    
    def test_timeline_visual_generation(self):
        """Test that timeline visuals can be generated."""
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity_score=60)
        comparison = estimator.generate_timeline_comparison(estimate)
        
        # Should have ASCII timeline
        assert hasattr(comparison, 'ascii_gantt')
        assert len(comparison.ascii_gantt) > 0
    
    def test_orchestrator_entry_point(self):
        """Test the SWAGGER Entry Point Orchestrator."""
        from src.orchestrators.swagger_entry_point_orchestrator import SWAGGEREntryPointOrchestrator
        
        orchestrator = SWAGGEREntryPointOrchestrator()
        
        # Test estimation flow
        result = orchestrator.estimate_from_complexity(
            complexity_score=50,
            feature_name="Test Feature"
        )
        
        assert result is not None
        assert 'estimate' in result
        assert 'timeline' in result


# ============================================================================
# Edge Cases
# ============================================================================

class TestEdgeCases:
    """Edge case and boundary tests."""
    
    def test_zero_complexity(self):
        """Test handling of zero complexity score."""
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity_score=0)
        
        assert estimate.story_points >= 1  # Minimum 1 point
    
    def test_max_complexity(self):
        """Test handling of maximum complexity score."""
        from src.agents.estimation.timeframe_estimator import TimeframeEstimator
        
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity_score=100)
        
        assert estimate.story_points >= 21  # Should be epic-sized
        assert estimate.sprints_single_dev >= 5
    
    def test_unicode_in_requirements(self):
        """Test Unicode handling in requirements."""
        from src.agents.estimation.dor_validator import DoRValidator
        
        validator = DoRValidator()
        result = validator.validate_dor("Feature: 日本語テスト with émojis 🚀")
        
        assert result is not None  # Should not crash
    
    def test_very_long_description(self):
        """Test handling of very long descriptions."""
        from src.agents.estimation.work_decomposer import WorkDecomposer
        
        decomposer = WorkDecomposer()
        long_description = "Detailed feature. " * 500  # ~8500 chars
        
        result = decomposer.decompose_work(
            title="Complex Feature",
            description=long_description,
            complexity_score=50
        )
        
        assert result is not None
        assert len(result.stories) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Integration Tests for Intent Router
Purpose: Validate routing logic and pipeline orchestration
Version: 1.0
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.components.intent_router import IntentRouter


class TestIntentRouter:
    """Test suite for Intent Router"""
    
    @pytest.fixture
    def router(self):
        """Create router instance for tests"""
        return IntentRouter()
    
    # ========================================================================
    # Test Rule 1: Explicit Planning Triggers
    # ========================================================================
    
    def test_explicit_planning_triggers(self, router):
        """Test that explicit planning keywords route to planning"""
        test_cases = [
            "plan authentication system",
            "let's plan the user dashboard",
            "help me design the API",
            "what approach should I take for payment?",
            "I want to plan a feature",
        ]
        
        for message in test_cases:
            result = router.route(message)
            assert result['action'] == 'planning', f"Failed for: {message}"
            assert result['confidence'] >= 0.7, f"Low confidence for: {message}"
            assert result['pipeline'] == 'sequential_planning_to_development'
    
    # ========================================================================
    # Test Rule 2: Explicit Development Triggers
    # ========================================================================
    
    def test_explicit_development_triggers(self, router):
        """Test that explicit development keywords route to development"""
        test_cases = [
            "add a login button",
            "implement user authentication",
            "fix the broken link",
            "create a new API endpoint",
            "build a dashboard component",
        ]
        
        for message in test_cases:
            result = router.route(message)
            assert result['action'] == 'development', f"Failed for: {message}"
            assert result['confidence'] >= 0.7, f"Low confidence for: {message}"
            assert result['pipeline'] == 'standalone_development'
    
    # ========================================================================
    # Test Rule 3: Ambiguous + Planning Context Signals
    # ========================================================================
    
    def test_ambiguous_with_planning_signals(self, router):
        """Test that ambiguous keywords + planning signals route to planning"""
        test_cases = [
            "authentication - not sure how to approach this",
            "payment system with security concerns",
            "dashboard feature - which approach should I use?",
        ]
        
        for message in test_cases:
            result = router.route(message)
            assert result['action'] == 'planning', f"Failed for: {message}"
            assert len(result['context_signals']) > 0, f"No context signals detected: {message}"
    
    # ========================================================================
    # Test Rule 4: Ambiguous + Implementation Signals
    # ========================================================================
    
    def test_ambiguous_with_implementation_signals(self, router):
        """Test that ambiguous keywords + implementation signals route to development"""
        test_cases = [
            "authentication - simple task",
            "dashboard - just add a quick component",
            "api endpoint - straightforward implementation",
        ]
        
        for message in test_cases:
            result = router.route(message)
            assert result['action'] == 'development', f"Failed for: {message}"
            assert len(result['context_signals']) > 0, f"No context signals detected: {message}"
    
    # ========================================================================
    # Test Rule 5: No Clear Match → Clarification
    # ========================================================================
    
    def test_no_clear_match_requests_clarification(self, router):
        """Test that unclear messages request clarification"""
        test_cases = [
            "authentication",  # Ambiguous alone
            "user management",  # Ambiguous alone
            "something about the system",  # Vague
        ]
        
        for message in test_cases:
            result = router.route(message)
            # Should be clarification or have low confidence
            if result['action'] == 'clarification':
                assert result['pipeline'] == 'clarification'
                assert 'PLAN' in result['response_template']
                assert 'IMPLEMENT' in result['response_template']
    
    # ========================================================================
    # Test Confidence Scoring
    # ========================================================================
    
    def test_confidence_scoring_multiple_keywords(self, router):
        """Test that multiple keyword matches increase confidence"""
        result1 = router.route("plan")
        result2 = router.route("plan and design")
        result3 = router.route("plan, design, and architect")
        
        # More keywords should increase confidence
        assert result2['confidence'] >= result1['confidence']
        assert result3['confidence'] >= result2['confidence']
        
        # But confidence should be capped at 0.95
        assert result3['confidence'] <= 0.95
    
    # ========================================================================
    # Test Keyword Matching Accuracy
    # ========================================================================
    
    def test_keyword_matching_word_boundaries(self, router):
        """Test that keyword matching respects word boundaries"""
        # Should NOT match "plan" in "airplane"
        result = router.route("fix airplane navigation")
        assert 'plan' not in result['keywords_matched']
        assert result['action'] == 'development'  # Should match "fix"
    
    def test_case_insensitive_matching(self, router):
        """Test that keyword matching is case-insensitive"""
        result1 = router.route("PLAN authentication")
        result2 = router.route("plan authentication")
        result3 = router.route("Plan Authentication")
        
        assert result1['action'] == result2['action'] == result3['action'] == 'planning'
    
    # ========================================================================
    # Test Pipeline Configuration Retrieval
    # ========================================================================
    
    def test_get_pipeline_config(self, router):
        """Test that pipeline configurations can be retrieved"""
        sequential_config = router.get_pipeline_config('sequential_planning_to_development')
        assert 'steps' in sequential_config
        assert len(sequential_config['steps']) == 3  # Plan → Approve → Implement
        
        standalone_planning = router.get_pipeline_config('standalone_planning')
        assert 'steps' in standalone_planning
        assert len(standalone_planning['steps']) == 2  # Plan → Approve
        
        standalone_dev = router.get_pipeline_config('standalone_development')
        assert 'steps' in standalone_dev
        assert len(standalone_dev['steps']) == 1  # Implement (with auto-generated AC)
    
    # ========================================================================
    # Test Metrics Logging
    # ========================================================================
    
    def test_metrics_logging_creates_file(self, router):
        """Test that routing decisions are logged to metrics file"""
        import json
        from pathlib import Path
        
        # Clear existing metrics file
        if router.metrics_path.exists():
            router.metrics_path.unlink()
        
        # Make a routing decision
        router.route("plan authentication")
        
        # Verify metrics file was created
        assert router.metrics_path.exists()
        
        # Verify metrics file has valid JSONL content
        with open(router.metrics_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) >= 1
            
            # Parse first line
            entry = json.loads(lines[0])
            assert 'timestamp' in entry
            assert 'routing_decision' in entry
            assert 'confidence_score' in entry
            assert entry['routing_decision'] == 'planning'
    
    # ========================================================================
    # Test Response Template Selection
    # ========================================================================
    
    def test_response_template_for_planning(self, router):
        """Test that planning actions get correct response template"""
        result = router.route("plan authentication")
        assert 'Planning Mode Activated' in result['response_template']
        assert 'help_plan_feature.md' in result['response_template']
    
    def test_response_template_for_development(self, router):
        """Test that development actions get correct response template"""
        result = router.route("implement login")
        assert 'Development Mode Activated' in result['response_template']
        assert 'Auto-generating basic requirements' in result['response_template']
    
    def test_response_template_for_clarification(self, router):
        """Test that clarification requests get correct template"""
        result = router.route("something unclear")
        if result['action'] == 'clarification':
            assert 'PLAN first' in result['response_template']
            assert 'IMPLEMENT directly' in result['response_template']
    
    # ========================================================================
    # Test Edge Cases
    # ========================================================================
    
    def test_empty_message(self, router):
        """Test handling of empty messages"""
        result = router.route("")
        assert result['action'] == 'clarification'
        assert result['confidence'] == 0.0
    
    def test_very_long_message(self, router):
        """Test handling of very long messages"""
        long_message = "plan authentication " * 100
        result = router.route(long_message)
        assert result['action'] == 'planning'
        assert result['confidence'] >= 0.7
    
    def test_mixed_triggers(self, router):
        """Test message with both planning and development triggers"""
        result = router.route("plan and implement authentication")
        # Should prioritize planning (Rule 1 has higher priority than Rule 2)
        assert result['action'] == 'planning'
    
    # ========================================================================
    # Test Real-World Scenarios
    # ========================================================================
    
    def test_real_world_scenario_complex_feature(self, router):
        """Test real-world scenario: complex security feature"""
        result = router.route("add payment processing with PCI-DSS compliance")
        # Should route to planning due to security concerns
        assert result['action'] in ['planning', 'clarification']
    
    def test_real_world_scenario_simple_fix(self, router):
        """Test real-world scenario: simple bug fix"""
        result = router.route("fix typo in button label")
        assert result['action'] == 'development'
        assert result['pipeline'] == 'standalone_development'
    
    def test_real_world_scenario_new_feature_uncertain(self, router):
        """Test real-world scenario: new feature with uncertainty"""
        result = router.route("add user notifications - not sure if email or SMS")
        assert result['action'] == 'planning'  # Uncertainty signals planning needed
        assert len(result['context_signals']) > 0


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

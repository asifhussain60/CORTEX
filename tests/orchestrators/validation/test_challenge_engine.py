"""
Tests for Challenge Engine (Phase 48 Stage 2)

Tests the generation of alternative approaches for IMPLEMENT/FIX/REFACTOR requests.
Ensures 3 alternatives with pros/cons/effort analysis and feasibility ranking.

Authority: PHASE-48-IMPLEMENTATION-PLAN.yaml Stage 2
Priority: P0-CRITICAL
AC-ID: AC-PHASE48-S2-TEST-001
"""

import pytest
from cortex.orchestrators.validation.challenge_engine import (
    ChallengeEngine,
    Challenge,
    AlternativeApproach,
)


class TestChallengeEngineInitialization:
    """Test Challenge Engine initialization and basic operations."""
    
    def test_engine_initializes_successfully(self):
        """Challenge engine should initialize without errors."""
        engine = ChallengeEngine()
        assert engine is not None
    
    def test_engine_has_generate_challenges_method(self):
        """Challenge engine should have generate_challenges method."""
        engine = ChallengeEngine()
        assert hasattr(engine, "generate_challenges")
        assert callable(engine.generate_challenges)


class TestChallengeGeneration:
    """Test challenge generation for different request types."""
    
    def test_generates_three_alternatives_for_implement_request(self):
        """Should generate exactly 3 alternative approaches."""
        engine = ChallengeEngine()
        request = "Implement user authentication with JWT tokens"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        assert len(challenge.alternatives) == 3
        assert all(isinstance(alt, AlternativeApproach) for alt in challenge.alternatives)
    
    def test_generates_three_alternatives_for_fix_request(self):
        """Should generate exactly 3 alternative fixes."""
        engine = ChallengeEngine()
        request = "Fix memory leak in data processing pipeline"
        intent = "FIX"
        
        challenge = engine.generate_challenges(request, intent)
        
        assert len(challenge.alternatives) == 3
    
    def test_generates_three_alternatives_for_refactor_request(self):
        """Should generate exactly 3 refactoring alternatives."""
        engine = ChallengeEngine()
        request = "Refactor monolithic service into microservices"
        intent = "REFACTOR"
        
        challenge = engine.generate_challenges(request, intent)
        
        assert len(challenge.alternatives) == 3
    
    def test_each_alternative_has_required_fields(self):
        """Each alternative should have title, description, pros, cons, effort."""
        engine = ChallengeEngine()
        request = "Implement caching layer for API"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        for alt in challenge.alternatives:
            assert hasattr(alt, "title")
            assert hasattr(alt, "description")
            assert hasattr(alt, "pros")
            assert hasattr(alt, "cons")
            assert hasattr(alt, "estimated_effort")
            assert len(alt.title) > 0
            assert len(alt.description) > 0
            assert len(alt.pros) > 0
            assert len(alt.cons) > 0
    
    def test_alternatives_include_pros_cons_analysis(self):
        """Each alternative should have at least 2 pros and 2 cons."""
        engine = ChallengeEngine()
        request = "Implement real-time notifications"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        for alt in challenge.alternatives:
            assert len(alt.pros) >= 2, f"Alternative '{alt.title}' has < 2 pros"
            assert len(alt.cons) >= 2, f"Alternative '{alt.title}' has < 2 cons"


class TestAlternativeDiversity:
    """Test that alternatives are meaningfully different."""
    
    def test_alternatives_have_different_titles(self):
        """Each alternative should have a unique title."""
        engine = ChallengeEngine()
        request = "Implement database connection pooling"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        titles = [alt.title for alt in challenge.alternatives]
        assert len(titles) == len(set(titles)), "Alternatives have duplicate titles"
    
    def test_alternatives_represent_different_approaches(self):
        """Alternatives should represent fundamentally different approaches."""
        engine = ChallengeEngine()
        request = "Implement user authentication"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        # Check that approaches are diverse (e.g., OAuth, JWT, session-based)
        descriptions = [alt.description.lower() for alt in challenge.alternatives]
        # At least one should mention a specific technology/pattern
        assert any("oauth" in desc or "jwt" in desc or "session" in desc for desc in descriptions)
    
    def test_fix_intent_generates_security_focused_alternatives(self):
        """FIX intent should generate security-aware alternatives when applicable."""
        engine = ChallengeEngine()
        request = "Fix SQL injection vulnerability in user search"
        intent = "FIX"
        
        challenge = engine.generate_challenges(request, intent)
        
        # At least one alternative should mention parameterized queries or ORM
        all_text = " ".join([
            f"{alt.title} {alt.description} {' '.join(alt.pros)}"
            for alt in challenge.alternatives
        ]).lower()
        
        assert any(keyword in all_text for keyword in [
            "parameterized", "prepared", "orm", "sanitize", "escape"
        ])


class TestEffortEstimation:
    """Test effort estimation for alternatives."""
    
    def test_effort_is_valid_time_estimate(self):
        """Effort should be a valid time estimate (e.g., '2 hours', '3 days')."""
        engine = ChallengeEngine()
        request = "Implement file upload functionality"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        for alt in challenge.alternatives:
            effort = alt.estimated_effort.lower()
            # Should contain time unit
            assert any(unit in effort for unit in ["hour", "day", "week", "minute"])
    
    def test_alternatives_have_varying_effort_levels(self):
        """Alternatives should have different effort levels (quick, moderate, complex)."""
        engine = ChallengeEngine()
        request = "Implement advanced search with filters"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        efforts = [alt.estimated_effort for alt in challenge.alternatives]
        # Should have at least 2 different effort estimates
        assert len(set(efforts)) >= 2, "All alternatives have same effort estimate"


class TestFeasibilityRanking:
    """Test feasibility ranking of alternatives."""
    
    def test_alternatives_are_ranked_by_feasibility(self):
        """Alternatives should be ordered by feasibility score (high to low)."""
        engine = ChallengeEngine()
        request = "Implement payment processing integration"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        for alt in challenge.alternatives:
            assert hasattr(alt, "feasibility_score")
            assert 0.0 <= alt.feasibility_score <= 1.0
        
        # Should be in descending order
        scores = [alt.feasibility_score for alt in challenge.alternatives]
        assert scores == sorted(scores, reverse=True), "Not sorted by feasibility"
    
    def test_recommended_alternative_has_highest_feasibility(self):
        """First alternative should be the recommended one (highest feasibility)."""
        engine = ChallengeEngine()
        request = "Implement logging framework"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        recommended = challenge.alternatives[0]
        assert recommended.feasibility_score == max(
            alt.feasibility_score for alt in challenge.alternatives
        )
    
    def test_challenge_includes_recommendation_explanation(self):
        """Challenge should explain why the first alternative is recommended."""
        engine = ChallengeEngine()
        request = "Implement error handling middleware"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        assert hasattr(challenge, "recommendation_explanation")
        assert len(challenge.recommendation_explanation) > 0
        assert "recommend" in challenge.recommendation_explanation.lower()


class TestIntentSpecificGeneration:
    """Test intent-specific challenge generation."""
    
    def test_implement_intent_focuses_on_design_patterns(self):
        """IMPLEMENT challenges should focus on architectural patterns."""
        engine = ChallengeEngine()
        request = "Implement event-driven notification system"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        
        all_text = " ".join([
            f"{alt.title} {alt.description}"
            for alt in challenge.alternatives
        ]).lower()
        
        # Should mention patterns/architectures or technical approaches
        assert any(keyword in all_text for keyword in [
            "pattern", "architecture", "design", "approach", "strategy",
            "websocket", "sse", "polling", "push", "real-time"
        ])
    
    def test_refactor_intent_focuses_on_code_quality(self):
        """REFACTOR challenges should focus on code quality improvements."""
        engine = ChallengeEngine()
        request = "Refactor legacy authentication module"
        intent = "REFACTOR"
        
        challenge = engine.generate_challenges(request, intent)
        
        all_text = " ".join([
            f"{alt.title} {alt.description} {' '.join(alt.pros)}"
            for alt in challenge.alternatives
        ]).lower()
        
        # Should mention quality attributes
        assert any(keyword in all_text for keyword in [
            "maintainability", "testability", "clean", "solid", "coupling", "cohesion"
        ])


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_handles_vague_requests_gracefully(self):
        """Should handle vague requests without crashing."""
        engine = ChallengeEngine()
        request = "Make it better"
        intent = "REFACTOR"
        
        # Should not raise exception
        challenge = engine.generate_challenges(request, intent)
        assert len(challenge.alternatives) == 3
    
    def test_handles_very_specific_requests(self):
        """Should handle highly specific technical requests."""
        engine = ChallengeEngine()
        request = "Implement Redis pub/sub for real-time chat with fallback to long-polling"
        intent = "IMPLEMENT"
        
        challenge = engine.generate_challenges(request, intent)
        assert len(challenge.alternatives) == 3
    
    def test_generates_challenges_for_unknown_intent_with_default_behavior(self):
        """Should use default behavior for unknown intents."""
        engine = ChallengeEngine()
        request = "Do something with the database"
        intent = "UNKNOWN"
        
        # Should not crash
        challenge = engine.generate_challenges(request, intent)
        assert len(challenge.alternatives) >= 1
